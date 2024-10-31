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


def list_algorithms(provider_id: str) -> None:
    """ List provider algoritms
    """
    from qgis.core import QgsApplication
    reg = QgsApplication.processingRegistry()

    provider = reg.providerById(provider_id)
    if provider is None:
        print("No provider '%s'" % provider_id)
        return False

    print('{: <50}{: <25}'.format("ID", "NAME"))
    for alg in provider.algorithms():
        print('{i: <50}{d: <25}'.format(i=alg.id(), d=alg.displayName()))
    return True


def list_providers(show_algorithms: bool = False) -> None:
    """ Display processing informations
    """
    from qgis.core import QgsApplication
    reg = QgsApplication.processingRegistry()

    if show_algorithms:
        print('{: <50}{: <25}'.format("ID", "NAME"))
        for provider in reg.providers():
            for alg in provider.algorithms():
                print('{i: <50}{d: <25}'.format(i=alg.id(), d=alg.displayName()))
    else:
        print('{: <20}{: <25}'.format("ID", "NAME"))
        for provider in reg.providers():
            print('{i: <20}{d: <25}'.format(i=provider.id(), d=provider.name()))
    return True


def show_alg_infos(algid: str) -> None:
    """ Display infos about an algorithm
    """
    from qgis.core import QgsApplication
    reg = QgsApplication.processingRegistry()

    alg = reg.algorithmById(algid)
    if alg is None:
        print(f"Algorithm '{algid}' not found", file=sys.stderr)
        return False

    print('\nNAME:\n', alg.id())
    print('\nDESCRIPTION:\n', alg.displayName(), '\n\n', alg.shortHelpString())
    print('\nPARAMETERS:')
    for p in alg.parameterDefinitions():
        dflt = p.defaultValue()
        print(
            '  {n: <25}{t: <20}{v: <10}{i: <10}{d}'.format(
                n=p.name(),
                d=p.description(),
                t=p.type(),
                i='dest' if p.isDestination() else '', v=dflt if dflt is not None else '',
            ),
        )
    return True


def processing_infos(argstring: str) -> None:
    """ Display processing informations
    """
    import argparse

    argv = argstring.split()

    parser = argparse.ArgumentParser(description='Display infos on processing algorithms')

    sub = parser.add_subparsers(title='commands', help='List algorithms')

    # List availables processings algorithms
    cmd = sub.add_parser('list', description="List processing algorithm")
    cmd.add_argument(
        '-P', '--providers',
        action='store_true',
        default=False,
        help="Show only providers",
        dest='providers',
    )
    cmd.set_defaults(command='list')

    # Display informations about one particular algorithm
    cmd = sub.add_parser('infos', description="Display information about one particular algorithm")
    cmd.add_argument('name', metavar='NAME', help="Name of the algorithm")
    cmd.set_defaults(command='infos')

    args = parser.parse_args(argv)

    if not hasattr(args, 'command'):
        parser.print_help()
        return

    if args.command == 'list':
        list_providers(not args.providers)
    elif args.command == 'infos':
        show_alg_infos(args.name)
