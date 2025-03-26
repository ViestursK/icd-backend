# development.py
from .base import *
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(BASE_DIR, '.env'))

DEBUG = True
SECRET_KEY = os.environ.get('SECRET_KEY', 'insecure-dev-key')
MORALIS_API_KEY = os.environ.get('MORALIS_API_KEY', '')

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# In backend/settings/development.py
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = [
    "https://iscryptodead.loca.lt",
    "http://localhost:3000",
    "https://icd-frontend-five.vercel.app"  # Add your frontend URL here
]
