from fastapi import FastAPI
from mongoApi import MongoDB
import smtplib
from passlib.context import CryptContext
import random
from pydantic import BaseModel, ValidationError


app = FastAPI()
dbase = MongoDB("", "", "")
gmail = smtplib.SMTP('smtp.gmail.com', 587)
gmail.login("ifs2343234@gmail.com", "ifs12345678")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
codes = {}

class Profile(BaseModel):
    id:int
    username:str
    password_hash:str
    email:str
    profile:dict
    integrations:list
    projects:list

example_profile = {
    "username": "user3",
    "password_hash": "$2a$12$GOiOy3Ll8S0DcraZ1plYPecEA/B3ubuWqWH1IZLqI6KQJEE88Rqzq",
    "email": "example@gmail.com",
    "profile": {
        "first_name": "First",
        "last_name": "User",
        "profile_picture": "",
        "status": "Lol1"
    },
    "integrations": [],
    "projects": []
}

@app.post("/api/auth/login")
def login(username:str, password:str):
    if not dbase.is_user(username):
        return -2
    user = dbase.find_by_username(username)
    if user["password_hash"] == get_password_hash(password):
        codes[user["username"]] = random.randint(100000, 999999)
        gmail.send_message("ifs2343234@gmail.com", user["email"], f"Confirmation code\n{codes[user['username']]}")
        return 0
    else:
        return -1

@app.post("/api/auth/confirm")
def confirm(username:str, code:int):
    if codes[username] == code:
        return "Success"
    else:
        return "Fail"

@app.post("/api/auth/register")
def register(username:str, password:str, email:str, first_name:str, last_name:str):
    if dbase.is_user(username):
        return -1
    try:
        user = Profile(4, username, get_password_hash(password), email, {first_name, last_name, "", ""}, [], [])
        dbase.create_user(user)
    except Exception as ex:
        print("[register] Some problem...")
        print(ex)

def get_password_hash(password):
    return pwd_context.hash(password)
