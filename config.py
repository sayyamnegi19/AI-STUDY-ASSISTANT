import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SAMESITE = "Lax"
    WTF_CSRF_TIME_LIMIT = None  #token stays valid for the whole session