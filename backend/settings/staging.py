from .base import *
import dj_database_url

print("LOADING STAGING SETTINGS")

# Debug could be enabled in staging for troubleshooting
DEBUG = True

# Use secret key from environment
SECRET_KEY = env('SECRET_KEY')

# Use development Moralis API key for staging
MORALIS_API_KEY = env('MORALIS_API_KEY_DEVELOP')

# Hardcoded allowed hosts
ALLOWED_HOSTS = ['icd-backend-develop-api.onrender.com']

# Database
database_url = env('DATABASE_URL')
DATABASES = {
    'default': dj_database_url.config(conn_max_age=600)
}

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# CORS settings - hardcoded
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    'https://icd-frontend-five.vercel.app',
]
CORS_ALLOW_CREDENTIALS = True

# Hardcoded trusted origins
CSRF_TRUSTED_ORIGINS = [
    'https://icd-backend-develop-api.onrender.com',
    'https://icd-frontend-five.vercel.app'
]

# Static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
