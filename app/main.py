from fastapi import FastAPI
from mongoApi import MongoDB
import smtplib
from passlib.context import CryptContext
import random
from pydantic import BaseModel, ValidationError
from datetime import datetime


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
        return "Invallid username or password"
    user = dbase.find_by_username(username)
    if user["password_hash"] == get_password_hash(password):
        return user
    else:
        return "Invallid username or password"

@app.post("/api/auth/confirm")
def confirm(username:str, code:int):
    time = datetime.now() - codes[username][1]
    if time.minute < 30 and time.hour == 0 and codes[username][0] == code:
        return dbase.find_by_username(username)
    else:
        return "Invallid code or more than 30 minutes have passed"

@app.post("/api/auth/register")
def register(username:str, password:str, email:str, first_name:str, last_name:str):
    if dbase.is_user(username):
        return "Username exists"
    try:
        user = Profile(4, username, get_password_hash(password), email, {first_name, last_name, "", ""}, [], [])
        dbase.create_user(user)
        codes[username] = [random.randint(100000, 999999), datetime.now()]
        gmail.send_message("ifs2343234@gmail.com", user["email"], f"Confirmation code\n{codes[username][0]}")
        return "Success"
    except Exception as ex:
        print("[register] Some problem...")
        print(ex)

def get_password_hash(password):
    return pwd_context.hash(password)
