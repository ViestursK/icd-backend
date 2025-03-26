import os

# Use the DJANGO_SETTINGS_MODULE environment variable directly
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', '')

if 'production' in settings_module:
    from .production import *
else:
    from .development import *

# Add this for debugging
import sys
print(f"Using settings module: {settings_module}", file=sys.stderr)
