# Configuration settings for the OSINT crawler app
import os

class Config:
    DEBUG = True
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
