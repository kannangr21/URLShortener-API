from datetime import date, time
from pydantic import BaseModel

class User(BaseModel):
    id : int
    userName : str
    fName : str
    lName : str
    email : str
    password : str

class Urls(BaseModel):
    userName : str
    longUrl : str
    shortUrl : str
    #count : int
    #date_created : date
    #time_created : time
