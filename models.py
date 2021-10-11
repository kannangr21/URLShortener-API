from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.types import Text, Date, Time
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
    count = Column(Integer)
    base64str = Column(Text)
    date_created = Column(Date)
    time_created = Column(Time)
    
    users = relationship("User", back_populates="urls")