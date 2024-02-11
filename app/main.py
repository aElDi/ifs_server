from fastapi import FastAPI
from .routers.authentication import authRouter

app = FastAPI()

app.include_router(authRouter, prefix="/api")
