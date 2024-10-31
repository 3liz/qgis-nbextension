#
#    qgis-nbextension
#    Copyright (C) 2019  David Marteau
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import os
import sys


def setup_qgis_paths() -> None:
    """ Init qgis paths
    """
    qgis_pluginpath = os.environ.get('QGIS_PLUGINPATH', '/usr/share/qgis/python/plugins/')
    sys.path.append(qgis_pluginpath)


# XXX Take care to keep a reference instance of the qgis_application object
# And not make this object garbage collected
_qgis_application: object = None


def start_qgis_application(
    enable_processing: bool = True,
    verbose: bool = False,
    cleanup: bool = True,
) -> object:
    """ Start qgis application

        :param boolean enable_processing: Enable processing, default to False
        :param boolean verbose: Output qgis settings, default to False
        :param boolean cleanup: Register atexit hook to close qgisapplication on exit().
            Note that prevents qgis to segfault when exiting. Default to True.
    """

    os.environ['QGIS_NO_OVERRIDE_IMPORT'] = '1'
    os.environ['QGIS_DISABLE_MESSAGE_HOOKS'] = '1'

    setup_qgis_paths()

    from qgis.core import Qgis, QgsApplication

    if QgsApplication.QGIS_APPLICATION_NAME != "QGIS3":
        raise RuntimeError(f"You need QGIS3 (found {QgsApplication.QGIS_APPLICATION_NAME})")

    #  We MUST set the QT_QPA_PLATFORM to prevent
    #  Qt trying to connect to display in containers
    if os.environ.get('DISPLAY') is None:
        print("Warning: Setting Qt offscreen mode")
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'

    qgis_prefix = os.environ.get('QGIS_HOME', '/usr')

    global _qgis_application

    if _qgis_application is not None:
        print("Qgis already initialized", file=sys.stderr, flush=True)
        return _qgis_application

    _qgis_application = QgsApplication([], False)

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

    print(f"Qgis {Qgis.QGIS_VERSION} initialized......")

    if enable_processing:
        init_processing()

    return _qgis_application


# Store if processing has been started
_qgis_processing_started = False


def init_processing():
    from processing.core.Processing import Processing
    from qgis.analysis import QgsNativeAlgorithms
    from qgis.core import QgsApplication

    global _qgis_processing_started

    if _qgis_processing_started:
        return

    QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
    Processing.initialize()
    _qgis_processing_started = True
    print("QGis processing initialized")


def install_logger_hook(verbose: bool = False) -> None:
    """ Install message log hook
    """
    from qgis.core import Qgis, QgsApplication
    # Add a hook to qgis  message log

    def writelogmessage(message, tag, level):
        arg = f"Qgis {tag}: {message}"
        if level in (Qgis.Warning, Qgis.Critical):
            print(arg, file=sys.stderr, flush=True)
        elif verbose:
            # Qgis is somehow very noisy
            # log only if verbose is set
            print(arg, flush=True)

    messageLog = QgsApplication.messageLog()
    messageLog.messageReceived.connect(writelogmessage)
