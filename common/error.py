'''
'''
from tornado.httputil import responses
RESPONSES = responses

from tornado.web import HTTPError


class IoTError(HTTPError):
    def __str__(self):
        message = "HTTP %d: %s" % (
            self.status_code, 
            self.reason or RESPONSES.get(self.status_code, 'Unkonwn'))
        if self.log_message:
            return message + " (" + (self.log_message % self.args) + ")"
        else:
            return message

class TokenError(HTTPError):
    pass

