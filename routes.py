from handler.tag import TagHandler
from handler.token import TokenHandler
from handler.things import ThingsHandler
from handler.corporation import  CorporationHandler
from handler.iot_id import  IotIDHandler,IotIDApplyHandler
from handler.account import  AccountHandler,AccountSupp
from handler.mobile_code import  MobileCodeHanlder
ROUTES = [
            (r'/tag/?$', TagHandler),
            (r'/things/?(.*)$', ThingsHandler),

            (r'/corporation/?(.*)$', CorporationHandler),

            (r'/iot_id/?(.*)$', IotIDHandler),
            (r'/id_application/?(.*)$', IotIDApplyHandler),

            (r'/account/?(.*)$', AccountHandler),
            (r'/supp_account/?(.*)$', AccountSupp),

            (r'/mobile_code/?(.*)$', MobileCodeHanlder),
            (r'/token/?$', TokenHandler),


            #(r'/iot_id_check/?$', IotIDCheckHandanler)
            # (r'/user/(.*)$', UserHandler),
            # (r'/pn/(.*)$', PnHandler),
            # in product environment, use nginx to support static resources
            # (r'/weixin', WeiXinHandler),
        ]