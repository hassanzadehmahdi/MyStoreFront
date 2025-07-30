from .common import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-axo$u3d@qrzi5h_k-#g!gn4f=n17uvazt1p64)wd9k0l#do0!('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mystorefront',
        'USER': 'postgres',
        'PASSWORD': 'gv2936',
        'HOST': '127.0.0.1',  # Or the IP address/hostname of your PostgreSQL server
        'PORT': '5432',       # Default PostgreSQL port
    }
}