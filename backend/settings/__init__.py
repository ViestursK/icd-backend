import os

# Default to local settings if not specified
environment = os.environ.get('DJANGO_ENVIRONMENT', 'local')

if environment == 'production':
    from .production import *
elif environment == 'staging':
    from .staging import *
else:
    from .local import *
