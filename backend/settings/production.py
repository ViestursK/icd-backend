# production.py
from .base import *
import os
import dj_database_url

DEBUG = False

# Make sure to set these in environment variables on your hosting provider
SECRET_KEY = os.environ.get('SECRET_KEY')
MORALIS_API_KEY = os.environ.get('MORALIS_API_KEY')

# Update with your actual domain
ALLOWED_HOSTS = [os.environ.get('ALLOWED_HOST', 'portfolio-tracker-api-173r.onrender.com')]

# Configure PostgreSQL using DATABASE_URL environment variable
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600
    )
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

# CORS settings - with proper domain handling
CORS_ALLOW_ALL_ORIGINS = False

# Process frontend domain to handle protocol and trailing slashes
frontend_domain = os.environ.get('FRONTEND_DOMAIN', 'icd-frontend-five.vercel.app')
if frontend_domain.endswith('/'):
    frontend_domain = frontend_domain.rstrip('/')
if frontend_domain.startswith('https://') or frontend_domain.startswith('http://'):
    # Domain already has protocol
    cors_frontend_url = frontend_domain
else:
    # Add protocol
    cors_frontend_url = f"https://{frontend_domain}"

# Process allowed host similarly
allowed_host = os.environ.get('ALLOWED_HOST', 'portfolio-tracker-api-173r.onrender.com')
if allowed_host.endswith('/'):
    allowed_host = allowed_host.rstrip('/')
if allowed_host.startswith('https://') or allowed_host.startswith('http://'):
    # Domain already has protocol
    cors_allowed_host = allowed_host
else:
    # Add protocol
    cors_allowed_host = f"https://{allowed_host}"

# Apply processed URLs
CORS_ALLOWED_ORIGINS = [cors_frontend_url]

# Also add localhost URLs for development if needed
CORS_ALLOWED_ORIGINS.extend([
    "http://localhost:5173",
    "http://localhost:3000"
])

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    cors_allowed_host,
    cors_frontend_url
]

# Static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
