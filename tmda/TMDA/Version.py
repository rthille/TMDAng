# -*- python -*-
#
# Copyright (C) 2001,2002 Jason R. Mastaler <jason@mastaler.com>
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

""" Various versioning information."""


import os
import sys


# TMDA version
TMDA = "0.49+"

# Python version
# e.g, 2.2 
PYTHON = sys.version.split()[0]

# System information
# e.g, ('OSF1', 'spe147', 'V5.1', '1885', 'alpha')
UNAME = os.uname()

# Platform identifier
# e.g, OSF1
PLATFORM = UNAME[0].replace(' ', '_')

# Machine architecture
# e.g, alpha
ARCH = UNAME[4].replace(' ', '_')

# Summary of all the version identifiers
# e.g, TMDA/0.49 (Python 2.2 on OSF1/alpha)
ALL = "TMDA/%s (Python %s on %s/%s)" % (TMDA, PYTHON, PLATFORM, ARCH)
