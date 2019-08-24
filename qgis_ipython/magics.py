#
# Copyright 2019 3liz
# Author: David Marteau
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import sys
import argparse
from typing import Tuple, Dict

from IPython.core.magic import Magics, line_magic, cell_magic, magics_class

from .startup import start_qgis_application
from .status  import processing_infos


def parse_args(argstring: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="qgis arguments")
    parser.add_argument("--verbose", action="store_true", default=False)
    parser.add_argument("--processing", action="store_true", default=False)
    args = parser.parse_args(argstring.split())

    return args


@magics_class
class QgisMagics(Magics):

    def __init__(self, shell: 'InteractiveShell' ) -> None:
        super().__init__(shell)
        self._inited = False

    @line_magic
    def qgis(self, line: str) -> None:
        """ Initialise qgis

            arguments:
                --verbose    : activate verbose mode
                --processing : enable qgis processing
        """
        args = parse_args(line)
        if self._inited:
            if args.verbose:
                print("Qgis already initialized",file=sys.stderr, flush=True)
            return

        start_qgis_application(verbose=args.verbose,enable_processing=args.processing)
        self._inited = True

    @line_magic('qgis-processing-infos')
    def qgis_processing_infos(self, line: str) -> None:
        if not self._inited:
            print("You must start qgis with '%qgis --processing' first.", file=sys.stderr, flush=True)
            return
        processing_infos(line)
        


