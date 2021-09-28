import random

import jwt
import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm.session import Session

import models
import schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "users/login")
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

@app.get("/")
def main():
    return {"detail":"Server is running"}

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
def user_login(uname : str, password : str,db : Session = Depends(get_db)):
    print("It comes here")
    db_user = db.query(models.User).filter(models.User.userName == uname).first()
    if db_user:
        if pwd_context.verify(password, db_user.password):
            token = jwt.encode({"userName" : db_user.userName, "email" : db_user.email}, JWT_SECRET)
           
            return db_user,{"access_token" : token, "token_type" : "bearer"}
        else:
            return {"Error":"Password Doesn't Match"}
    db.close()
    return {"Error" : "User Doesn't Exist"}

async def current_user(token : str = Depends(oauth2_scheme), db : Session = Depends(get_db)):
    payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    user = db.query(models.User).filter(models.User.userName == payload.get('userName')).first()
    return user

@app.post("/users/update/")
def user_update(user = Depends(current_user)):
    return user

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
def url_create(uname : str, longUrlin : str, db : Session = Depends(get_db)):
    while(True):
        sURL = to_base_62()
        db_sURL = db.query(models.Urls).filter(models.Urls.shortUrl == sURL).first()
        if db_sURL:
            continue
        else:
            return add_URL(uname, longUrlin, sURL, db)

@app.post("/urls/addUrl/customize")
def url_create(uname : str, longUrlin : str, sURL : str, db : Session = Depends(get_db)):
    db_sURL = db.query(models.Urls).filter(models.Urls.shortUrl == sURL).first()
    if db_sURL:
        return {"error" : "Short URL exists already"}
    else:
        return add_URL(uname, longUrlin, sURL, db)


@app.get("/{shortURL}")
def redirect_original(shortURL : str, db : Session = Depends(get_db)):
    db_url = db.query(models.Urls).filter(models.Urls.shortUrl == shortURL).first()
    if db_url:
        return RedirectResponse(db_url.longUrl)
    else:
        return { "error" : "Something"}
    

if __name__ == "__main__":
    uvicorn.run(app, DEBUG = True)
