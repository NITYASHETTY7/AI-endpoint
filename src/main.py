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

app = FastAPI()                                                              #app initialization

@app.get("/")                
async def root():
   return {"message":"Welcome to the AI Endpoint,login and start chatting with AI!"}

#creating user endpoint and hashing password
pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto") 
@app.post("/users/register", response_model=schemas.ShowUser, tags=['Sign Up'])
def register_user(request: schemas.User):
    hashedPassword = pwd_cxt.hash(request.password)
    new_user = schemas.User(id=request.id, name=request.name, email=request.email, password=hashedPassword)
    users.append(new_user)
    return schemas.ShowUser(name=new_user.name, email=new_user.email)

# Token endpoint: authenticate against users list
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = next((u for u in users if u.name == form_data.username), None)
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
async def get_all_users():
    return {'all_users':users}


@app.get("/users/{user_id}", response_model=schemas.ShowUser,tags=['Sign Up'])  # Endpoint to show user details
def get_a_user(user_id: int):
    for user in users:
        if user.id == user_id:
            return schemas.ShowUser(name=user.name, email=user.email)
    return {"error": "User not found"}
