
# imports

import random
from datetime import datetime

from sqlalchemy.sql.functions import user

import jwt
import pyqrcode
import uvicorn
from dateutil.tz import gettz
from decouple import config
from fastapi import Depends, FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext
from sqlalchemy.orm.session import Session

import models
import schemas
from database import SessionLocal, engine
from util import OAuth2PasswordBearerWithCookie

# Database / JWT Authentication / Password Encryption

models.Base.metadata.create_all(bind=engine)  
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl = "users/login")
JWT_SECRET = config('JWT_SECRET')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# app initialization

app = FastAPI()

# CORS

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connection with the database

def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.close()

# Endpoints

'''
'/',                          # Root 
'/users/create' ,             # Creates users
'/users/login' ,              # Login, sets cookie / returns url list
'/users/profile' ,            # Retruns user profile / url list
'/users/profile/update' ,     # Returns user's updated profile
'/urls/addUrl' ,              # Creates random short url with QR code (base64 string)
'/urls/addUrl/customize' ,    # Creates customized short url with QR code (base64 string)
'/users/logout' ,             # Logout, deletes cookie
'/{shortURL}'                 # Redirects to original (Long) URL
'''

@app.get("/")
def main():
    return {"detail":"Server is running"}

@app.post("/users/create")
async def create_user(user : schemas.User, db : Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.userName == user.userName).first()
    if db_user:
        return {"Error" : "Username Already Exists"}
    db_add_user = models.User(
        id = user.id,
        userName = user.userName,
        fName = user.fName,
        lName = user.lName,
        email = user.email,
        password = pwd_context.hash(user.password)
    )
    db.add(db_add_user)
    db.commit()
    db.close()
    return {"detail" : "User Created Successfully"}

@app.post("/users/login")
async def user_login(response : Response, uname : str, password : str,db : Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.userName == uname).first()
    if db_user:
        if pwd_context.verify(password, db_user.password):
            user_urls = db.query(models.Urls).filter(models.Urls.userName == uname).all()
            token = jwt.encode({"userName" : db_user.userName, "email" : db_user.email}, JWT_SECRET)
            response.set_cookie(key = "access_token", value = f"Bearer {token}")
            for url in user_urls:
                url.date_created = url.date_created.strftime("%d %b %Y")
                url.time_created = url.time_created.strftime("%I:%M %p")   
            return user_urls
        else:
            return {"Error" : "Invalid credentials"}
    db.close()
    return {"Error" : "User Doesn't Exist"}

# Checks cookie and authorizes current user

async def current_user(token : str = Depends(oauth2_scheme), db : Session = Depends(get_db)):
    payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    user = db.query(models.User).filter(models.User.userName == payload.get('userName')).first()
    return user

@app.post("/users/profile")
async def user_update(current_user : schemas.User = Depends(current_user),  db : Session = Depends(get_db)):
    if current_user:
        user_urls = db.query(models.Urls).filter(models.Urls.userName == current_user.userName).all()
        for url in user_urls:
            url.date_created = url.date_created.strftime("%d %b %Y")
            url.time_created = url.time_created.strftime("%I:%M %p") 
    return current_user, user_urls

@app.post("/users/profile/update")
async def user_update(current_user : schemas.User = Depends(current_user)):
    return current_user

# Converts the longURL to a short code

async def to_base_62():
    deci = random.randint(1,9999999)
    s = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    hash_str = ''
    while (deci>0):
       hash_str= s[deci % 62] + hash_str
       deci //= 62
    return hash_str

# Adds the shortCode and longURL to the database 

def add_URL(uname, longUrlin, sURL, db):
    QRcode = pyqrcode.create("http://127.0.0.1:8000/" + sURL)
    b64Format = QRcode.png_as_base64_str(scale=5)
    dtobj = datetime.now(tz=gettz('Asia/Kolkata'))
    db_add_url = models.Urls(
    userName = uname,
    longUrl = longUrlin,
    shortUrl = sURL,
    count = 0,
    base64str = b64Format,
    date_created = datetime.date(dtobj),
    time_created = datetime.time(dtobj)    
    )
    db.add(db_add_url)
    db.commit()
    db.close()
    return {"detail" : "URL Added",
            "Short Code" : sURL,
            "QRCode" : b64Format}
     
@app.post("/urls/addUrl")
async def url_create(longUrlin : str, db : Session = Depends(get_db), current_user : schemas.User = Depends(current_user)):
    if current_user:
        while(True):
            sURL = await to_base_62()
            db_sURL = db.query(models.Urls).filter(models.Urls.shortUrl == sURL).first()
            if db_sURL:
                continue
            else:
                return add_URL(current_user.userName, longUrlin, sURL, db)                
    else:
        return {"error" : "User not logged in"}

@app.post("/urls/addUrl/customize")
async def url_create(longUrlin : str, sURL : str, db : Session = Depends(get_db), current_user : schemas.User = Depends(current_user)):
    if current_user:
        db_sURL = db.query(models.Urls).filter(models.Urls.shortUrl == sURL).first()
        if db_sURL:
            return {"error" : "Short URL exists already"}
        else:
            return add_URL(current_user.userName, longUrlin, sURL, db)
    else:
        return {"error" : "User not logged in"}

@app.get("/users/logout")
def user_logout(response: Response, current_user : schemas.User = Depends(current_user)):
    response.delete_cookie("access_token")
    return {"detail" : "Logged out successfully"}

@app.get("/{shortURL}")
def redirect_original(shortURL : str, db : Session = Depends(get_db)):
    db_url = db.query(models.Urls).filter(models.Urls.shortUrl == shortURL).first()
    if db_url:
        db_url.count = db_url.count + 1
        db.commit()
        return RedirectResponse(db_url.longUrl)
    else:
        return {"error" : "Something"}
    
if __name__ == "__main__":
    uvicorn.run(app, DEBUG = True)