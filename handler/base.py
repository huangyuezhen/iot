'''
'''
from __future__ import absolute_import, division, print_function, with_statement

# standrad libary

import sys
import  json

# Tornado framework
import tornado.web
HTTPError = tornado.web.HTTPError

import tornado.ioloop
import tornado.auth
import tornado.escape
import tornado.options
import tornado.locale
import tornado.httpclient
import tornado.gen
import tornado.httputil
from tornado.log import access_log

from common import util
from common import error

json_encoder = util.json_encoder
json_decoder = util.json_decoder

from db import  mariadb


class BaseHandler(tornado.web.RequestHandler):
    '''
        BaseHandler
        override class method to adapt special demands
    '''
    OK = {'code':200, 'msg':'OK'}
    RESPONSES = error.responses
    def initialize(self):
        pass

    def options(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Contro-Allow-Methods', "PUT")
        self.add_header('Access-Contro-Allow-Methods', "POST")
        self.add_header('Access-Control-Allow-Methods', "DELETE")
        #self.set_header('Access - Control - Allow - Methods', "POST")

        self.set_header('Access-Control-Allow-Headers','x-requested-with,content-type')

    def _get_argument(self, name, default, source, strip=True):
        args = self._get_arguments(name, source, strip=strip)
        if not args:
            if default is self._ARG_DEFAULT:
                raise tornado.web.MissingArgumentError(name)
            return default
        return args[0]

    def set_status(self, status_code, reason=None):
        '''
            Set custom error resson
        '''
        self._status_code = status_code
        self._reason = 'Unknown Error'
        if reason is not None:
            self._reason = tornado.escape.native_str(reason)
        else:
            try:
                self._reason = self.RESPONSES[status_code]
            except KeyError:
                raise ValueError('Unknown status code {}'.format(status_code))

    def write_error(self, status_code, **kwargs):
        
            #Customer error return format
        if self.settings.get('debug') and 'exc_info' in kwargs:
            self.set_header('Content-Type', 'text/plain')
            import traceback
            for line in traceback.format_exception(*kwargs['exc_info']):
                self.write(line)
            self.finish()
        else:
            self.render_json_response(code=status_code, msg=self._reason)

    def _handle_request_exception(self, e):
        if isinstance(e, tornado.web.Finish):
            # not an error; just finish the request without loggin.
            if not self._finished:
                self.finish(*e.args)
            return
        try:
            self.log_exception(*sys.exc_info())
        except Exception:
            access_log.error('Error in exception logger', exc_info=True)

        if self._finished:
            return 
        if isinstance(e, HTTPError):
            if e.status_code not in self.RESPONSES and not e.reason:
                tornado.gen_log.error('Bad HTTP status code: %d', e.status_code)
                self.send_error(500, exc_info=sys.exc_info())
            else:
                self.send_error(e.status_code, exc_info=sys.exc_info())
        else:
            self.send_error(500, exc_info=sys.exc_info())

    def log_exception(self, typ, value, tb):
        if isinstance(value, HTTPError):
            if value.log_message:
                format = '%d %s: ' + value.log_message
                args = ([value.status_code, self._request_summary()] + list(value.args))
                access_log.warning(format, *args)

        access_log.error('Exception: %s\n%r', self._request_summary(), 
                     self.request, exc_info=(typ, value, tb))
    

    def render_exception(self, ex):
        self.set_status(ex.status_code)
        self.render('error.html', code=ex.status_code, msg=ex.reason)

    def render_json_response(self, **kwargs):
        '''
            Encode dict and return response to client
        '''
        callback = self.get_argument('callback', None)
        if callback:
            # return jsonp
            self.set_status(200, kwargs.get('msg', None))
            self.finish('{}({})'.format(callback, json_encoder(kwargs)))
        else:
            self.set_status(kwargs['code'], kwargs.get('msg', None))
            self.set_header('Content-Type', 'application/json;charset=utf-8')
            self.finish(json_encoder(kwargs))

    def prepare(self):
        '''
            check client paltform
        '''

        session = mariadb.connect()
        if not session:
            raise HTTPError(500, 'session is none')
        self.session = session()

        # try to parse request body
        self._parse_body()


    def on_finish(self):
        '''
        '''
        if self.session:
            self.session.close()



    def _parse_body(self):
        '''
            1. request body: support json, convert single value to tuple

        '''
        content_type = self.request.headers.get('Content-Type', '')
        # parse json format arguments in request body content
        if content_type.startswith('application/json') and self.request.body:
            try :
                arguments = json_decoder(tornado.escape.native_str(self.request.body))
            except json.decoder.JSONDecodeError:
                """invalid  json arguments"""
                raise error.IoTError(400, reason="JSONDecodeError,invalid json arguments")
            else:
                for name, values in arguments.items():
                    if isinstance(values, str) :
                        values = [values, ]
                    elif isinstance(values, int) or isinstance(values, float) :
                        values = [str(values), ]
                    elif values:
                        values = [v for v in values if v]

                    if values:
                        self.request.arguments.setdefault(name, []).extend(values)

