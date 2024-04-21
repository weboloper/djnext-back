from .base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost","127.0.0.1"]

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
# ]
CORS_ALLOW_ALL_ORIGINS = True


# CSRF_TRUSTED_ORIGINS =[
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
# ]

# Add your media root
MEDIA_ROOT = os.path.join(CONTENT_DIR, 'media')
# Define the URL for media files
MEDIA_URL = '/media/'