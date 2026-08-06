import os

import sqlalchemy
import sqlalchemy.orm

# CHANGE echo=True to False when deploying
engine = sqlalchemy.create_engine(os.environ["DATABASE_URL"], echo=True)

session_creator = sqlalchemy.orm.sessionmaker(bind=engine)


def get_db():
    db = session_creator()
    try:
        yield db
    finally:
        db.close()
