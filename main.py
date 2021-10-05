import random

import jwt
import uvicorn
from fastapi import Depends, FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from util import OAuth2PasswordBearerWithCookie
from passlib.context import CryptContext
from sqlalchemy.orm.session import Session

import models
import schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl = "users/login")
JWT_SECRET = "AsecretKeyTobeSecret"
app = FastAPI()
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

def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.close()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#homepage
@app.get("/")
def main():
    return {"detail":"Server is running"}

#create user
@app.post("/users/create")
def create_user(user : schemas.User, db : Session = Depends(get_db)):
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
def user_login(response : Response, uname : str, password : str,db : Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.userName == uname).first()
    if db_user:
        if pwd_context.verify(password, db_user.password):
            user_urls = db.query(models.Urls).filter(models.Urls.userName == uname).all()
            token = jwt.encode({"userName" : db_user.userName, "email" : db_user.email}, JWT_SECRET)
            response.set_cookie(key = "access_token", value = f"Bearer {token}")   
            return user_urls
        else:
            return {"Error":"Password Doesn't Match"}
    db.close()
    return {"Error" : "User Doesn't Exist"}

async def current_user(token : str = Depends(oauth2_scheme), db : Session = Depends(get_db)):
    payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    user = db.query(models.User).filter(models.User.userName == payload.get('userName')).first()
    return user

@app.post("/users/profile")
def user_update(current_user : schemas.User = Depends(current_user)):
    return current_user

@app.post("/users/profile/update")
def user_update(current_user : schemas.User = Depends(current_user)):
    return current_user

def to_base_62():
    deci = random.randint(1,10)
    s = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    hash_str = ''
    while (deci>0):
       hash_str= s[deci % 62] + hash_str
       deci //= 62
    return hash_str

def add_URL(uname, longUrlin, sURL, db):
    db_add_url = models.Urls(
    userName = uname,
    longUrl = longUrlin,
    shortUrl = sURL
    #count = 0,
    #date_created = "Today",
    #time_created = "12:00:00"    
    )
    db.add(db_add_url)
    db.commit()
    db.close()
    return {"detail" : "URL Added",
            "Short Code" : sURL}
  
@app.post("/urls/addUrl")
def url_create(longUrlin : str, db : Session = Depends(get_db), current_user : schemas.User = Depends(current_user)):
    if current_user:
        while(True):
            sURL = to_base_62()
            db_sURL = db.query(models.Urls).filter(models.Urls.shortUrl == sURL).first()
            if db_sURL:
                continue
            else:
                return add_URL(current_user.userName, longUrlin, sURL, db)
    else:
        return {"error" : "User not logged in"}

@app.post("/urls/addUrl/customize")
def url_create(longUrlin : str, sURL : str, db : Session = Depends(get_db), current_user : schemas.User = Depends(current_user)):
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
        return RedirectResponse(db_url.longUrl)
    else:
        return { "error" : "Something"}
    

if __name__ == "__main__":
    uvicorn.run(app, DEBUG = True)
