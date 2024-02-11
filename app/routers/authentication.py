from random import randint
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import JSONResponse
from ..config import GMAIL_EMAIL, GMAIL_PASSWORD
from ..db.RedisDB import redisdb
from ..models.User import User
from ..db.MongoDB import db
from passlib.context import CryptContext
from smtplib import SMTP_SSL
import secrets

authRouter = APIRouter(
    prefix="/auth",
    tags=['auth'],
    # responses={
    #     400: "Bad request",
    #     404: "User not found",
    #     403: "Incorrect password",
    #     408: "Code is timeout"
    # }
)

mail = SMTP_SSL('smtp.yandex.ru')
mail.login(GMAIL_EMAIL, GMAIL_PASSWORD)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def gen_randkey():
    return secrets.token_hex(16)

@authRouter.post("/login")
def login(username:str, password:str):

    if not db.is_user(username=username):
        raise HTTPException(404, f"Not found user {username}")
    
    user = db.find_by_username(username) # User object from database

    if get_password_hash(password) == user["password_hash"]:
        return {"status": "OK"}
    
    raise HTTPException(403, f"Incorrect password")
    
    
@authRouter.post("/confirm")
def confirm(rayid:str, code:int):
    try:
        confirm_code = redisdb.getConfirmRay(rayid)
        if code == confirm_code:
            db.change_user(confirm_code["username"], "email_confirmed", True)
            redisdb.removeConfirmRay(rayid)
            return "OK"
        else: 
            raise HTTPException(401, "Incorrect code")
    except Exception as ex:
        print('[authRouter] Confirm code error')
        print(ex)


@authRouter.post("/register")
def register(username:str, password:str, email:str, first_name:str, last_name:str):
    if db.is_user(username):
        raise HTTPException(400, "Username allready uses")
    try:
        user = User(username=username, password_hash=get_password_hash(password), email=email, email_confirmed=False, profile={"first_name": first_name, "last_name": last_name, "status": "", "profile_picture": ""}, projects=set(), integrations=set())
        db.create_user(user)
        ray_id = gen_randkey()
        conf_code = randint(1000,9999)
        mail.sendmail(GMAIL_EMAIL, email, f"Your confirmation key:\n<b>{conf_code}</b>")
        redisdb.addConfirmRay(ray_id, conf_code, username)
        return {"ray_id": ray_id}
    except Exception as ex:
        print("[authRouter] Register error")
        print(ex)