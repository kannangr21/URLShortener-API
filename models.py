from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Time
from sqlalchemy.types import Date
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "UserDetails"

    id = Column(Integer)
    userName = Column(String, primary_key=True, unique=True)
    fName = Column(String)
    lName = Column(String)
    email = Column(String)
    password = Column(String)

    urls = relationship("Urls", back_populates="users")

class Urls(Base):
    __tablename__ = "UserURLs"
    id = Column(Integer, primary_key=True)
    userName = Column(String, ForeignKey('UserDetails.userName'))
    longUrl = Column(String)
    shortUrl = Column(String, unique=True)
    #count = Column(Integer)
    #date_created = Column(String)
    #time_created = Column(Time)
    ''' Database to be modified
    Test : Old database to be deleted and check for a new one!
    Id not a field in old db'''

    users = relationship("User", back_populates="urls")