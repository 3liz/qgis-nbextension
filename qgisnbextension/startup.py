#
# Copyright 2019 3liz
# Author: David Marteau
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import sys

def darwin_setup() -> None:
    """ Set up environment variables for OSX
    """
    prefix = os.environ.get('QGIS_PREFIX','/Applications')
    if not os.path.exists('%s/QGIS.app' % prefix):
        raise FileNotFoundError('%s/QGIS.app' % prefix)
    os.environ['QGIS_HOME'] = '%s/QGIS.app/Contents/MacOS' % prefix
    os.environ['QGIS_PLUGINPATH'] =  '%s/QGIS.app/Contents/Resources/python/plugins' % prefix
    # Set up qgis python bindings path
    sys.path.append('%s/QGIS.app/Contents/Resources/python' % prefix)


def setup_qgis_paths() -> None:
    """ Init qgis paths
    """
    if os.uname()[0].lower() == 'darwin':
        darwin_setup()
    qgis_pluginpath = os.environ.get('QGIS_PLUGINPATH','/usr/share/qgis/python/plugins/')
    sys.path.append(qgis_pluginpath)


#XXX Take care to keep a reference instance of the qgis_application object
# And not make this object garbage collected
_qgis_application = None


def start_qgis_application(enable_gui: bool=False, enable_processing: bool=True, verbose: bool=False,
                           cleanup: bool=True) -> 'QgsApplication':
    """ Start qgis application

        :param boolean enable_gui: Enable graphical interface, default to False
        :param boolean enable_processing: Enable processing, default to False
        :param boolean verbose: Output qgis settings, default to False
        :param boolean cleanup: Register atexit hook to close qgisapplication on exit().
            Note that prevents qgis to segfault when exiting. Default to True.
    """

    os.environ['QGIS_NO_OVERRIDE_IMPORT']    = '1'
    os.environ['QGIS_DISABLE_MESSAGE_HOOKS'] = '1'

    setup_qgis_paths()

    from qgis.core import QgsApplication, Qgis

    if QgsApplication.QGIS_APPLICATION_NAME != "QGIS3":
        raise RuntimeError("You need QGIS3 (found %s)" % QgsApplication.QGIS_APPLICATION_NAME)

    if not enable_gui:
        #  We MUST set the QT_QPA_PLATFORM to prevent
        #  Qt trying to connect to display in containers
        if os.environ.get('DISPLAY') is None:
            print("Warning: Setting Qt offscreen mode")
            os.environ['QT_QPA_PLATFORM'] = 'offscreen'

    qgis_prefix = os.environ.get('QGIS_HOME','/usr')

    global _qgis_application

    if _qgis_application is not None:
        print("Qgis already initialized",file=sys.stderr, flush=True)
        return _qgis_application

    _qgis_application = QgsApplication([], enable_gui )

    # Install logger hook
    install_logger_hook(verbose=verbose)

    _qgis_application.setPrefixPath(qgis_prefix, True)
    _qgis_application.initQgis()

    if cleanup:
        # Closing QgsApplication on exit will
        # prevent our app to segfault on exit()
        import atexit

        @atexit.register
        def exitQgis():
            global _qgis_application
            if _qgis_application:
                _qgis_application.exitQgis()
                del _qgis_application

    if verbose:
        print(_qgis_application.showSettings())

    if enable_processing:
        init_processing(verbose)

    if verbose:
        print("Qgis %s initialized......" % Qgis.QGIS_VERSION)

    return _qgis_application


def init_processing(verbose: bool=False):
    from processing.core.Processing import Processing
    from qgis.analysis import QgsNativeAlgorithms
    from qgis.core import QgsApplication
    QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
    Processing.initialize()
    if verbose:
        print("QGis processing initialized")


def install_logger_hook( verbose: bool=False ) -> None:
    """ Install message log hook
    """
    from qgis.core import Qgis, QgsApplication, QgsMessageLog
    # Add a hook to qgis  message log
    def writelogmessage(message, tag, level):
        arg = 'Qgis {}: {}'.format( tag, message )
        if level in (Qgis.Warning, Qgis.Critical):
            print(arg,file=sys.stderr,flush=True)
        elif verbose:
            # Qgis is somehow very noisy
            # log only if verbose is set
            print(arg, flush=True)

    messageLog = QgsApplication.messageLog()
    messageLog.messageReceived.connect( writelogmessage )

