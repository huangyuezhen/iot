#!/usr/bin/python3
'''
'''
from __future__ import absolute_import, division, print_function, with_statement

# Tornado framework
import tornado.web
HTTPError = tornado.web.HTTPError

import tornado.ioloop
from tornado.log import app_log
# from tornado.concurrent import Future

from tornado.options import define, options

import os


from conf import settings
serve_config = settings['serve']

from common import util

# from handler.geo import GeoCodeHandler

from routes import ROUTES

# MOBILE_PATTERN = re.compile(r'^(?:13[0-9]|14[57]|15[0-35-9]|17[678]|18[0-9])\d{8}$')

class Application(tornado.web.Application):
    '''
        Web application class.
        Redefine __init__ method.
    '''

    _STATIC_PATH_ = settings['serve']['static_path']

    # _STATIC_PATH_ = settings['serve']['static_path']
    def __init__(self):
        settings = {

            'cookie_secret':util.sha1('iot_serve').hexdigest(),
            'static_path':self._STATIC_PATH_,
            # 'static_url_prefix':'resource/',
            #'debug':False,
            'cookie_secret':util.sha1('iot_serve').hexdigest(), 
            'static_path':serve_config['static_path'],
            # 'static_url_prefix':'resource/',
            'debug':serve_config['debug'],

            'autoreload':True,
            'autoescape':'xhtml_escape',
            'i18n_path':os.path.join(serve_config['static_path'], 'resource/i18n'),
            # 'login_url':'',
            'xheaders':True,    # use headers like X-Real-IP to get the user's IP address instead of
                                # attributeing all traffic to the balancer's IP address.
        }
        '''
        settings = {
            'debug': True,
            #'autoreload': True

        }'''
        super(Application, self).__init__(ROUTES, **settings)

def main():
    # log configuration
    define('port', default=7880, help='running on the given port', type=int)

    tornado.options.parse_command_line(final=False)
    # log rotate by time (day), max save 3 files
    options.log_rotate_mode = 'time'
    options.log_file_num_backups = 3
    options.logging = 'debug' if serve_config['debug'] else 'info'
    options.log_to_stderr = serve_config['debug']
    options.log_file_prefix = '{}/{}.log'.format(serve_config['log_path'], options.port)
    # define('log_file_prefix', type=str, default='{}/{}.log'.format(serve_config['log_path'], options.port))
    options.run_parse_callbacks()

    # init_log(config['log_folder'], config['logging_config'], options.port)

    portal_pid = os.path.join(settings['serve']['run_path'], 'p_{}.pid'.format(options.port))
    with open(portal_pid, 'w') as f:
        f.write('{}'.format(os.getpid()))

    # init db
    #import db
    #db_config = settings['database']
    #conn, db_kwargs = db_config.pop('conn'), db_config
    #db.connect(conn, **db_kwargs)
    #db.connect()
    #db.connect(conn)

    # import totoro
    # totoro.setup_producer()

    app = Application()
    app.listen(options.port, xheaders=app.settings.get('xheaders', False), decompress_request=True)
    #io_loop = tornado.ioloop.IOLoop.instance()
    #io_loop = tornado.ioloop.PollIOLoop.instance()


    # from common import token_formatters
    # # rotate fernet each 30 minutes
    # tornado.ioloop.PeriodicCallback(token_formatters.rotate_keys, 30*60*1000).start()

    app_log.info('IoT Server Listening:{} Started'.format(options.port))
    print("iot_server is starting ..")
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
