import config
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
from flask_sqlalchemy import SQLAlchemy

c = config.Config()
engine = create_engine(c.postgres_uri, echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()




def init_app(app):
    #app.register_blueprint(db_session, url_prefix='/app_db/db')
    db = SQLAlchemy(app)
    # any other Blueprint-specific initializations can go here
    return db


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    Base.metadata.create_all(bind=engine)


def select_all(User):
    all_users = db_session.query(User).all()

    for user in all_users:
        print(user.id, user.email, user.username)


def drop_tables():
    Base.metadata.drop_all(engine)



