import os
import bcrypt
import secrets, string
from sqlalchemy import create_engine, Column, String, DateTime, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# Define the base class
Base = declarative_base()

# Define the APIKey class
class APIKey(Base):
    __tablename__ = 'api_keys'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    expiration_date = Column(DateTime, nullable=False)
    role = Column(String, default='user')

# Create an engine
engine = create_engine(os.getenv('DATABASE_URL'), echo=True, future=True)

# Create all tables in the database which are defined by Base's subclasses
Base.metadata.create_all(engine)

# Create a sessionmaker bound to this engine
Session = sessionmaker(bind=engine, future=True)

def generate_api_key(length=32):
    # Define the characters that can be used in the API key
    characters = string.ascii_letters + string.digits
    # Generate a random string of the specified length
    api_key = ''.join(secrets.choice(characters) for _ in range(length))
    return api_key

def add_api_key(key, expiration_date):
    # Retrieve username
    session = Session()
    keys = session.query(APIKey).filter().all()
    username = "null"
    role="user"
    for db_key in keys:
        found = bcrypt.checkpw(key.encode('utf-8'), db_key.api_key.encode('utf-8'))
        if found is True:
            username = db_key.username
            role = db_key.role
            break
    if username in ["null"]:
        # TODO return a proper error object
        raise Exception("key has no username.")
    salt = bcrypt.gensalt()
    api_key = generate_api_key()
    hashed = bcrypt.hashpw(api_key.encode('utf-8'), salt)
    new_key = APIKey(username=username, salt=salt.decode('utf-8'), api_key=hashed.decode('utf-8'), expiration_date=expiration_date, role=role)
    session.add(new_key)
    session.commit()
    session.close()
    return api_key

def validate_api_key(api_key):
    session = Session()
    keys = session.query(APIKey).filter().all()
    found = False
    for key in keys:
        found = bcrypt.checkpw(api_key.encode('utf-8'), key.api_key.encode('utf-8'))
        if found is True:
            break
    session.close()
    return found

def get_api_keys(username, api_key):
    session = Session()

    keys = session.query(APIKey).filter(APIKey.username == username).all()
    found = False
    for db_key in keys:
        found = bcrypt.checkpw(api_key.encode('utf-8'), db_key.api_key.encode('utf-8'))
        if found is True:
            break
    if found is False:
        # TODO return a proper error object
        raise Exception("API Key belongs to another user.")

    session.close()
    return keys

def delete_api_key(key_id, api_key):
    session = Session()

    keys = session.query(APIKey).filter().all()
    username = "null"
    for db_key in keys:
        found = bcrypt.checkpw(api_key.encode('utf-8'), db_key.api_key.encode('utf-8'))
        if found is True:
            username = db_key.username
            break
    if username in ["null"]:
        # TODO return a proper error object
        raise Exception("key has no username.")

    key = session.query(APIKey).filter(APIKey.id == key_id and APIKey.username == username).first()
    if key:
        session.delete(key)
        session.commit()
        session.close()
        return True
    session.close()
    return False

