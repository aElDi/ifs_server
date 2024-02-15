from random import randint
from fastapi import APIRouter, HTTPException
from ..config import GMAIL_EMAIL, GMAIL_PASSWORD
from ..db.RedisDB import redisdb
from ..models.User import User
from ..db.MongoDB import db
from passlib.context import CryptContext
from smtplib import SMTP_SSL
from email.mime.multipart import MIMEMultipart
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
pwd_context = CryptContext(schemes=["bcrypt"])

def get_password_hash(password):
    return pwd_context.hash(password, salt="d"*21+"1")

def gen_randkey():
    return secrets.token_hex(16)

@authRouter.post("/login")
def login(username:str, password:str):

    if not db.is_user(username=username):
        raise HTTPException(404, f"Not found user {username}")
    
    user = db.find_by_username(username) # User object from database
    print(get_password_hash(password), user['password_hash'])
    if get_password_hash(password) == user["password_hash"]:
        return {"status": "OK"}
    
    raise HTTPException(403, f"Incorrect password")
    
    
@authRouter.post("/confirm")
def confirm(rayid:str, code:str):
    try:
        confirm_code = redisdb.getConfirmRay(rayid)
        print(confirm_code)
        if code == confirm_code["conf_code"]:
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
        mail_msg = MIMEMultipart()
        mail_msg['From']    = GMAIL_EMAIL                       # Адресат
        mail_msg['To']      = email                             # Получатель
        mail_msg['Subject'] = 'Confirm code'                    # Тема сообщения
        mail_msg.attach(f"Your confirmation key:\n<b>{conf_code}</b>", "html", "utf-8")
        mail.send_message(mail_msg)
        redisdb.addConfirmRay(ray_id, conf_code, username)
        return {"ray_id": ray_id}
    except Exception as ex:
        print("[authRouter] Register error")
        print(ex)