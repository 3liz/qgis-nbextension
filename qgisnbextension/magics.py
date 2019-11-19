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
        


