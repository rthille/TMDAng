# -*- python -*-
#
# Copyright (C) 2001,2002 Jason R. Mastaler <jason@mastaler.com>
#
# Author: Tim Legant <tim@catseye.net>
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

"""TMDA Address objects."""

import re
import time

import email

import Cookie
import Defaults
from Errors import *


# Private helper functions
def _split(address):
    local_parts = []
    local = ''
    domain = ''
    if address:
        at = address.rindex('@')
        local = address[:at].lower()
        domain = address[at+1:].lower()
        local_parts = local.split(Defaults.RECIPIENT_DELIMITER)
    return local_parts, local, domain


# Address classes

class Address:
    def __init__(self, address=''):
        self.address = address

    def base(self):
        return Defaults.USERNAME + '@' + Defaults.HOSTNAME
                        
    def create(self, base):
        self.address = base or self.base()

    def verify(self):
        raise BadCryptoError, "No cryptographic information in address."

    def split(self):
        (dummy, local, domain) = _split(self.address)
        return local, domain

    def tag(self):
        return ''

    def __str__(self):
        return self.address


class TaggedAddress(Address):
    def __init__(self, address):
        Address.__init__(self, address)
        (self.local_parts, dummy, dummy) = _split(address)

    def tag(self):
        return self.local_parts[1]


class ConfirmAddress(TaggedAddress):
    def __init__(self, address=''):
        TaggedAddress.__init__(self, address)

    def create(self, base, timestamp, pid, keyword):
        if Defaults.CONFIRM_ADDRESS:
            base = Defaults.CONFIRM_ADDRESS
        elif not base:
            base = self.base()
        (dummy, local, domain) = _split(str(base))
        cookie = Cookie.make_confirm_cookie(int(timestamp), pid, keyword)
        self.local_parts = [ local, 'confirm', keyword + '.' + cookie ]
        tagged_local = Defaults.RECIPIENT_DELIMITER.join(self.local_parts)
        self.address = tagged_local + '@' + domain
        return self

    def verify(self, dummy=''):
        try:
            (keyword, timestamp, pid, hmac) = self.local_parts[-1].split('.')
            try_hmac = Cookie.confirmationmac(timestamp, pid, keyword)
            if try_hmac != hmac:
                raise BadCryptoError, "Invalid cryptographic tag."
        except ValueError:
            raise BadCryptoError, "Invalid cryptographic tag format."

    def keyword(self):
        return self.local_parts[-1].split('.')[0]

    def timestamp(self):
        return self.local_parts[-1].split('.')[1]

    def pid(self):
        return self.local_parts[-1].split('.')[2]

    def hmac(self):
        return self.local_parts[-1].split('.')[3]


class DatedAddress(TaggedAddress):
    def __init__(self, address=''):
        TaggedAddress.__init__(self, address)

    def create(self, base, timeout=None):
        if not base:
            base = self.base()
        (dummy, local, domain) = _split(str(base))
        cookie = Cookie.make_dated_cookie(int(time.time()), timeout)
        self.local_parts = [ local, 'dated', cookie ]
        tagged_local = Defaults.RECIPIENT_DELIMITER.join(self.local_parts)
        self.address = tagged_local + '@' + domain
        return self

    def verify(self, dummy=''):
        try:
            (timestamp, hmac) = self.local_parts[-1].split('.')
            try_hmac = Cookie.datemac(timestamp)
            if int(time.time()) > int(timestamp):
                raise ExpiredAddressError, "Dated address has expired."
            if try_hmac != hmac:
                raise BadCryptoError, "Invalid cryptographic tag."
        except ValueError:
            raise BadCryptoError, "Invalid cryptographic tag format."

    def timestamp(self, prettyprint = 0, localtime = 0):
        expires = self.local_parts[-1].split('.')[0]

        if not prettyprint:
            return expires

        expires = int(expires)
        if localtime:
            local_tz = time.strftime("%Z", time.localtime(expires))
            expires_str = time.asctime(time.localtime(expires)) + ' ' + local_tz
        else:
            expires_str = time.asctime(time.gmtime(expires)) + ' UTC'
        return expires_str

    def hmac(self):
        return self.local_parts[-1].split('.')[1]


class KeywordAddress(TaggedAddress):
    def __init__(self, address=''):
        TaggedAddress.__init__(self, address)

    def create(self, base, keyword):
        if not base:
            base = self.base()
        (dummy, local, domain) = _split(str(base))
        cookie = Cookie.make_keyword_cookie(keyword)
        self.local_parts = [ local, 'keyword', cookie ]
        tagged_local = Defaults.RECIPIENT_DELIMITER.join(self.local_parts)
        self.address = tagged_local + '@' + domain
        return self

    def verify(self, dummy=''):
        parts = self.local_parts[-1].split('.')
        keyword = '.'.join(parts[:-1])
        if not keyword:
            raise BadCryptoError, "Invalid cryptographic tag format."
        hmac = parts[-1]
        try_hmac = Cookie.make_keywordmac(keyword)
        if try_hmac != hmac:
            raise BadCryptoError, "Invalid cryptographic tag."

    def tag(self):
        return 'keyword'

    def keyword(self):
        return '.'.join(self.local_parts[-1].split('.')[:-1])

    def hmac(self):
        return self.local_parts[-1].split('.')[-1]


class SenderAddress(TaggedAddress):
    def __init__(self, address=''):
        TaggedAddress.__init__(self, address)

    def create(self, base, sender):
        if not base:
            base = self.base()
        (dummy, local, domain) = _split(str(base))
        cookie = Cookie.make_sender_cookie(str(sender))
        self.local_parts = [ local, 'sender', cookie ]
        tagged_local = Defaults.RECIPIENT_DELIMITER.join(self.local_parts)
        self.address = tagged_local + '@' + domain
        return self

    def verify(self, sender):
        hmac = self.local_parts[-1]
        try_hmac = Cookie.make_sender_cookie(str(sender).lower())
        if try_hmac != hmac:
            raise BadCryptoError, "Invalid cryptographic tag."

    def hmac(self):
        return self.local_parts[-1]



def Factory(address = None, tag = None):
    """Create an address object of the appropriate class."""
    if tag:
        pass
    elif address:
        address = email.Utils.parseaddr(address)[1]
        (local_parts, dummy, dummy) = _split(address)
    else:    
        return Address(address)
    try:
        cookie_type = tag or local_parts[-2]
        if cookie_type == 'confirm':
            addr_obj = ConfirmAddress(address)
        elif cookie_type == 'dated':
            addr_obj = DatedAddress(address)
        elif cookie_type == 'sender':
            addr_obj = SenderAddress(address)
        else:
            addr_obj = KeywordAddress(address)
    except (AddressError, IndexError):
        addr_obj = Address(address)
    return addr_obj