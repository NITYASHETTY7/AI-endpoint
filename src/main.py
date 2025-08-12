import os
from fastapi import Depends, FastAPI
from pydantic import BaseModel
from .ai.gemini import Gemini
from .auth.dependencies import get_user_identifier
from .auth.throttling import apply_rate_limit

app = FastAPI()                                                              #app initialization

def load_system_prompt():                                                    #ai configuration
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

@app.post("/chat",response_model=chatResponse)                               #api endpoint
async def chat(request : chatRequest, user_id : str = Depends(get_user_identifier)):
    apply_rate_limit(user_id)
    response_text = ai_platform.chat(request.prompt)
    return chatResponse(response = response_text)


@app.get("/")
async def root():
   return {"message": "API is running"}