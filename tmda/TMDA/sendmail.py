#!/usr/bin/env python
#
# Copyright (C) 2001-2007 Jason R. Mastaler <jason@mastaler.com>
#
# This file is part of TMDA.
#
# TMDA is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.  A copy of this license should
# be included in the file COPYING.
#
# TMDA is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with TMDA; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

"""
Sendmail compatibility wrapper.

Usage:  %(program)s [ -t ] [ -fsender ] [ -Fname ] [ arg ... ]
"""

import getopt
import os
import sys

from . import Version
from .Util import runcmd


def usage(code, msg=''):
    print(__doc__ % globals())
    if msg:
        print(msg)
    sys.exit(code)


def main():
    header_recipients = None
    arglist = ['']

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   'Vhvimte:f:p:o:B:F:EJx', ['version',
                                                             'help'])
    except getopt.error as msg:
        usage(1, msg)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage(0)
        elif opt == '-V':
            print(Version.ALL)
            sys.exit()
        elif opt == '--version':
            print(Version.TMDA)
            sys.exit()
        elif opt == '-t':
            header_recipients = True
        elif opt == '-F':
            os.environ['NAME'] = arg

    # If recipients are provided as args, pass them to tmda-inject
    # unless `-t' was specified.
    if args and not header_recipients:
        arglist += args

    runcmd(sys.excutable, '-m', 'TMDA.inject', *arglist)


# This is the end my friend.
if __name__ == '__main__':
    main()
