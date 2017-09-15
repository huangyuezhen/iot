# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import base64
import datetime
import struct
import urllib.parse

from cryptography import fernet



from tornado.log import app_log

from . import fernet_utils

from .error import TokenError
from .util import json_encoder, json_decoder


# Fernet byte indexes as computed by pypi/keyless_fernet and defined in
# https://github.com/fernet/spec
TIMESTAMP_START = 1
TIMESTAMP_END = 9

fernet_conf = {
    'key_repository':'conf.d/fernet',
    'max_active_keys':1,
}

class TokenFormatter(object):
    """Packs and unpacks payloads into tokens for transport."""
    def __init__(self, key_repository='conf.d/fernet', max_active_keys=3):
        self.fernet_utils = fernet_utils.FernetUtils(
            fernet_conf['key_repository'],
            fernet_conf['max_active_keys'],
            'fernet_tokens'
        )
        self.keys = []
        self.multi_fernet = None

    def load_keys(self, reload_=False):
        if self.keys and not reload_:
            return self.keys
        keys = self.fernet_utils.load_keys()
        if not keys:
            raise TokenError(500, 'key not founds')
        self.keys = keys
       # print(self.keys)
        self.fernet_instances = [fernet.Fernet(key) for key in keys]
        fernet_instances = [fernet.Fernet(key) for key in keys]
        self.multi_fernet = fernet.MultiFernet(fernet_instances)

    def rotate_keys(self):
        self.fernet_utils.rotate_keys()
        self.load_keys(reload_=True)

    @property
    def crypto(self):
        """Return a cryptography instance.

        You can extend this class with a custom crypto @property to provide
        your own token encoding / decoding. For example, using a different
        cryptography library (e.g. ``python-keyczar``) or to meet arbitrary
        security requirements.

        This @property just needs to return an object that implements
        ``encrypt(plaintext)`` and ``decrypt(ciphertext)``.

        """
        return self.multi_fernet 

    def pack(self, payload):
        """Pack a payload for transport as a token.

        :type payload: six.binary_type
        :rtype: six.text_type

        """
        # base64 padding (if any) is not URL-safe
        return self.crypto.encrypt(payload).rstrip(b'=').decode('utf-8')

    def unpack(self, token):
        """Unpack a token, and validate the payload.

        :type token: six.text_type
        :rtype: six.binary_type

        """
        # TODO(lbragstad): Restore padding on token before decoding it.
        # Initially in Kilo, Fernet tokens were returned to the user with
        # padding appended to the token. Later in Liberty this padding was
        # removed and restored in the Fernet provider. The following if
        # statement ensures that we can validate tokens with and without token
        # padding, in the event of an upgrade and the tokens that are issued
        # throughout the upgrade. Remove this if statement when Mitaka opens
        # for development and exclusively use the restore_padding() class
        # method.
        if token.endswith('%3D'):
            token = urllib.parse.unquote(token)
        else:
            token = TokenFormatter.restore_padding(token)

        try:
            return self.crypto.decrypt(token.encode('utf-8'))
        except fernet.InvalidToken:
            raise TokenError('401', 'This is not a recognized Fernet token %s', token)

    @classmethod
    def restore_padding(cls, token):
        """Restore padding based on token size.

        :param token: token to restore padding on
        :type token: six.text_type
        :returns: token with correct padding

        """
        # Re-inflate the padding
        mod_returned = len(token) % 4
        if mod_returned:
            missing_padding = 4 - mod_returned
            token += '=' * missing_padding
        return token

    @classmethod
    def creation_time(cls, fernet_token):
        """Return the creation time of a valid Fernet token.

        :type fernet_token: six.text_type

        """
        fernet_token = TokenFormatter.restore_padding(fernet_token)
        # fernet_token is six.text_type

        # Fernet tokens are base64 encoded, so we need to unpack them first
        # urlsafe_b64decode() requires six.binary_type
        token_bytes = base64.urlsafe_b64decode(fernet_token.encode('utf-8'))

        # slice into the byte array to get just the timestamp
        timestamp_bytes = token_bytes[TIMESTAMP_START:TIMESTAMP_END]

        # convert those bytes to an integer
        # (it's a 64-bit "unsigned long long int" in C)
        timestamp_int = struct.unpack(">Q", timestamp_bytes)[0]

        # and with an integer, it's trivial to produce a datetime object
        issued_at = datetime.datetime.utcfromtimestamp(timestamp_int)

        return issued_at

    def create_token(self, **kwargs):
        """
            Given a set of payload attributes, generate a Fernet token.
            expires_at : expired datetime (%Y-%m-%d %H:%M:%S)
        """
        
        data = json_encoder(kwargs)

        serialized_payload = data.encode('utf-8')

        token = self.pack(serialized_payload)

        # NOTE(lbragstad): We should warn against Fernet tokens that are over
        # 255 characters in length. This is mostly due to persisting the tokens
        # in a backend store of some kind that might have a limit of 255
        # characters. Even though Keystone isn't storing a Fernet token
        # anywhere, we can't say it isn't being stored somewhere else with
        # those kind of backend constraints.
        if len(token) > 255:
            app_log.warning('Fernet token created with length of %d '
                            'characters, which exceeds 255 characters', len(token))

        return token

    def validate_token(self, token, request=None):
        """Validate a Fernet token and returns the payload attributes.
        request : httprequest, check remote_ip  if request given

        :type token: six.text_type
        """
        serialized_payload = self.unpack(token)

        payload = json_decoder(serialized_payload.decode('utf-8'))

        if 'expires_at' in payload:
            expires_at = payload['expires_at']
            expired = datetime.datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S')
            if datetime.datetime.now() > expired:
                raise TokenError(401, 'Token expired at %s, login again.', expires_at)

        if 'remote_ip' in payload and request:
            if payload['remote_ip'] != request.remote_ip:
                raise TokenError(401, 'client enviorment changed, login again.', expires_at)

        return payload


import sys
fernet_keys = TokenFormatter()
fernet_keys.load_keys()
sys.modules[__name__] = fernet_keys

