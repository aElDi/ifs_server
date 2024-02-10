from pydantic import BaseModel

class User(BaseModel):
    username:str
    password_hash:str
    email:str
    email_confirmed: bool
    profile:dict
    integrations:set
    projects:set
    