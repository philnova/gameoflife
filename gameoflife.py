from application import Application, handlers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import os

app = Application(handlers, config=os.environ, debug=True)
db = app.db
development = app.development

#some_engine = create_engine(os.environ.get('DATABASE_URL'))
#Session = sessionmaker(bind=some_engine)
#session = Session()

login_session = app.login_session
client_id = app.google_client_id

engine = create_engine(os.environ['DATABASE_URL'])
Base = declarative_base()
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()