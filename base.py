import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

url = os.environ["DATABASE_URL"]
# create an engine
engine = create_engine(url)

# create a configured "Session" class
Session = sessionmaker(bind=engine)

Base = declarative_base()
