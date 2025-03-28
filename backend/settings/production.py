from .base import *
import dj_database_url

print("LOADING PRODUCTION SETTINGS")

# No debug in production
DEBUG = False

# Use secret key from environment
SECRET_KEY = env('SECRET_KEY')

# Use production Moralis API key
MORALIS_API_KEY = env('MORALIS_API_KEY_PRODUCTION')

# Hardcoded allowed hosts
ALLOWED_HOSTS = ['icd-backend-production-api.onrender.com', 'api.iscryptodead.io']

# Database
database_url = env('DATABASE_URL')
DATABASES = {
    'default': dj_database_url.config(conn_max_age=600)
}

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'

# CORS settings - hardcoded
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    'https://iscryptodead.io',
    'https://www.iscryptodead.io'
]
CORS_ALLOW_CREDENTIALS = True

# Hardcoded trusted origins
CSRF_TRUSTED_ORIGINS = [
    'https://icd-backend-production-api.onrender.com',
    'https://api.iscryptodead.io',
    'https://iscryptodead.io',
    'https://www.iscryptodead.io'
]

# Static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
