import os
from fastapi import Depends, FastAPI
from pydantic import BaseModel
from .ai.gemini import Gemini
from .auth.dependencies import *
from .auth.throttling import apply_rate_limit

from . import schemas
from passlib.context import CryptContext

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

from . import schemas, models           ##db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

app = FastAPI()                                                              #app initialization

@app.get("/")                
async def root():
   return {"message":"Welcome to the AI Endpoint,login and start chatting with AI!"}

DATABASE_URL = os.getenv("MYSQL_URL")    ##db
if not DATABASE_URL:
    raise ValueError("MYSQL_URL environment variable not set")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#creating user endpoint and hashing password
pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto") 
@app.post("/users/register", response_model=schemas.ShowUser, tags=['Sign Up'])
def register_user(request: schemas.User, db: SessionLocal = Depends(get_db)):  # Add db dependency
    hashedPassword = pwd_cxt.hash(request.password)
    db_user = models.User(name=request.name, email=request.email, password=hashedPassword)    # save to MySQL instead of in-memory lis
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return schemas.ShowUser(name=db_user.name, email=db_user.email)


# Token endpoint: authenticate against users list
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: SessionLocal = Depends(get_db)):  ##db
    user = db.query(models.User).filter(models.User.name == form_data.username).first()                 ##db.
    if not user or not pwd_cxt.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    to_encode = {"sub": user.name}
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire.timestamp()})
    access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_token, "token_type": "bearer"}


def load_system_prompt():                                                   #ai configuration
    try :
       with open("/workspaces/AI-endpoint/src/prompts/system_prompt.md","r") as f:
            return f.read()
    except FileNotFoundError:
        return None
    
system_prompt = load_system_prompt()
gemini_api_key = os.getenv("GEMINI_API_KEY")  
if not gemini_api_key:
    raise ValueError("gemini_api_key environment variable not set")

ai_platform = Gemini(api_key = gemini_api_key,system_prompt=system_prompt)

class chatRequest(BaseModel):                                                #pydantic models
    prompt : str

class chatResponse(BaseModel):
    response : str 

@app.post("/chat",response_model=chatResponse,tags=['AI to the Rescue'])                               #api endpoint
async def chat(request : chatRequest, user_id : str = Depends(get_user_identifier)):
    apply_rate_limit(user_id)
    response_text = ai_platform.chat(request.prompt)
    return chatResponse(response = response_text)


from typing import List
#get all users
users: List[schemas.User] = []
@app.get("/users",tags=['Sign Up'])
async def get_all_users(db: SessionLocal = Depends(get_db)):  ##db
    users = db.query(models.User).all() 


@app.get("/users/{user_id}", response_model=schemas.ShowUser,tags=['Sign Up'])  # Endpoint to show user details
def get_a_user(user_id: int, db: SessionLocal = Depends(get_db)):               ##db
    user = db.query(models.User).filter(models.User.id == user_id).first()  
    if not user:
        return {"error": "User not found"}
    return schemas.ShowUser(name=user.name, email=user.email)


##for deployment
import uvicorn
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
