from pydantic import BaseModel

#user fields
class User(BaseModel):
    id :int
    name:str
    email:str
    password:str

#showing only email and name
class ShowUser(BaseModel):
    name:str
    email:str

    class Config:
        orm_mode = True  # This allows the model to work with ORM objects
