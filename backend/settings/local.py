from .base import *

# Debug mode enabled for local development
DEBUG = True

# Use development key from .env 
SECRET_KEY = env('SECRET_KEY')

# Use development Moralis API key
MORALIS_API_KEY = env('MORALIS_API_KEY_DEVELOP')

# Allow local hosts
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Local database (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS settings for local development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]
