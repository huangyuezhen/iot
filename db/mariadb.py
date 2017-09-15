

from sqlalchemy import create_engine, orm
from contextlib import contextmanager
import sqlalchemy

from conf import settings
from common.error import IoTError

db_config = settings['database']
DB_URL, db_kwargs = db_config.pop('conn'), db_config
ENGINE = create_engine(DB_URL, **db_kwargs)


SESSION = None

def connect(engine =ENGINE):
    '''
        uri: dialect+driver://user:password@host:port/dbname[?key=value...]
        kwargs: reference sqlalchemy.create_engine
    '''
    global SESSION
    if not SESSION:
        #engine = create_engine(uri, **kwargs)
        SESSION = orm.sessionmaker(bind=engine)
    return SESSION

@contextmanager
def session_scope(session):
    '''
        caller create new session & close created session
        caller control session scope:
            request scope
            application scope
    '''
    try:
        yield session
        session.commit()
    except sqlalchemy.exc.IntegrityError:
        session.rollback()
        raise  IoTError(400,reason= "Duplicate  error")
    except:
        session.rollback()
        raise
    finally:
        pass











