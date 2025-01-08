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

# Create an engine
engine = create_engine(os.getenv('DATABASE_URL'), echo=True, future=True)
print(str(os.getenv('POSTGRESQL_SCHEME')))
print(str(os.getenv('POSTGRESQL_USERNAME')))
print(str(os.getenv('POSTGRESQL_HOST')))
print(str(os.getenv('POSTGRESQL_PORT')))
print(str(os.getenv('POSTGRESQL_PATH')))

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

def add_api_key(username, expiration_date):
    session = Session()
    salt = bcrypt.gensalt()
    api_key = generate_api_key()
    hashed = bcrypt.hashpw(api_key.encode('utf-8'), salt)
    new_key = APIKey(username=username, salt=salt.decode('utf-8'), api_key=hashed.decode('utf-8'), expiration_date=expiration_date)
    session.add(new_key)
    session.commit()
    session.close()
    return api_key

def validate_api_key(api_key):
    session = Session()
    
    # First we have to get the salt
    keys = session.query(APIKey).filter().all()
    found = False
    for key in keys:
        print(f"key: {key}")
        hashed_api_key = bcrypt.hashpw(api_key.encode('utf-8'), key.salt.encode('utf-8'))
        key = session.query(APIKey).filter(APIKey.api_key == hashed_api_key.decode('utf-8')).first()
        if key is not None:
            found = True
            break
    session.close()
    return found

def get_api_keys(username):
    session = Session()
    keys = session.query(APIKey).filter(APIKey.username == username).all()
    session.close()
    return keys

def delete_api_key(username, api_key_id):
    session = Session()
    key = session.query(APIKey).filter(APIKey.id == api_key_id, APIKey.username == username).first()
    if key:
        session.delete(key)
        session.commit()
        session.close()
        return True
    session.close()
    return False

