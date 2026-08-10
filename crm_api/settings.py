from pathlib import Path
from datetime import timedelta
import multiprocessing
import os

if os.name == 'nt':
    multiprocessing.set_start_method('spawn', force=True)
    
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-5fq5en44!hn66a@t+z-#wx_3+df*+14mtx-oz+85v4oeg2nr-3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "*",
    "127.0.0.1",
    "localhost",
    "autopilot-elude-ungloved.ngrok-free.dev",
]

# 🌐 100% CORS Permission Allowed for Frontend
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = ["*"]
CORS_ALLOW_METHODS = ["*"]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://trench-probing-decimeter.ngrok-free.dev",
    "https://unaligned-faceted-gander.ngrok-free.dev",
    "https://autopilot-elude-ungloved.ngrok-free.dev",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "https://*.ngrok-free.dev",
    "https://autopilot-elude-ungloved.ngrok-free.dev",
]

# Application definition
INSTALLED_APPS = [
    'daphne',
    'corsheaders',
    'telecalling',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'utils',
    'channels',
    'huey.contrib.djhuey',
    "adm"
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'crm_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',  # 👈 .django. சேர்க்கப்பட்டது
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ASGI_APPLICATION = 'crm_api.asgi.application'
WSGI_APPLICATION = 'crm_api.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'crm_testing_db',
        'USER': 'postgres',
        'PASSWORD': 'Siva@2002',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'  # ✅ IST
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# 👈 Media files (Excel Exports & Uploads Settings)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication User model
AUTH_USER_MODEL = 'telecalling.User'

# Rest framework exception handler
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'utils.exceptions.api_exception_handler',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

# SIMPLE JWT Configurations
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=15),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer', 'JWT'),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'uid',
}

ACCESS_TOKEN_GENERIC_LIFETIME = timedelta(days=1)       
ACCESS_TOKEN_MOBILE_LIFETIME = timedelta(days=30)

# Huey Async Tasks
HUEY = {
    'name': 'crm',
    'result_store': True,
    'events': True,
    'store_none': False,
    'immediate': False,
    'store_errors': True,
    'blocking': False,
    'backend_class': 'huey.RedisHuey',
    'connection': {
        'host': 'localhost',
        'port': 6379,
        'db': 1,
        'connection_pool': None,
    },
    'consumer': {
        'workers': 1,
        'worker_type': 'thread',
        'initial_delay': 0.1,
        'backoff': 1.15,
        'max_delay': 10.0,
        'utc': False,
        'timezone': 'Asia/Kolkata',
        'scheduler_interval': 1,
        'periodic': True,
        'check_worker_health': True,
        'health_check_interval': 1,
    },
    'utc': False,
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

WHATSAPP_ACCESS_TOKEN = "EAASZAQf0nOkYBRQhOBDGNiTj7cSXk7dZBHxbVYvBrQPFHZCwtpPHj2dW6Co5Rnnpb0ixKmK5QQZCLsadp7Fk69MB9efgzYvunNloyKRf9LcZA0H3ow1nT60C5ZBEPHluGveO8Ws0FQOH7t5yDumZC4tXj1aHEZAUisByDAQUGCqYXe3rkQhuxZBt5Ry3ZBYbfCnecACAiG3ovontJWGU7rDDA21mmsmABGp6kzjWaUv4H7vEq8onHNZBdN5RKmVsVeCcA8nHZBtKuFpgjiQ5g6gkcI0b5kXb"
WHATSAPP_PHONE_NUMBER_ID = "1082538808272517"
WEBHOOK_VERIFY_TOKEN = "mysecret123"