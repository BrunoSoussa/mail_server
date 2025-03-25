import os
from datetime import timedelta

class Config:
    SECRET_KEY = 'dev-secret-key-123'
    JWT_SECRET_KEY = 'dev-jwt-secret-key-456'
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    CORS_RESOURCES = {
        r"/api/*": {
            "origins": ["http://localhost:5000"],
            "methods": ["GET", "POST"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    }
