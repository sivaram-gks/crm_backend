from pathlib import Path
from datetime import timedelta
import multiprocessing
import os
# from corsheaders.defaults import default_headers

if os.name == 'nt':
    
    multiprocessing.set_start_method('spawn',force=True)
    
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-5fq5en44!hn66a@t+z-#wx_3+df*+14mtx-oz+85v4oeg2nr-3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# CORS_ALLOW_CREDENTIALS = True 
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'trench-probing-decimeter.ngrok-free.dev',
    'unaligned-faceted-gander.ngrok-free.dev'
]

CORS_ALLOW_ALL_ORIGINS = False


# CORS_ALLOW_HEADERS = list(default_headers) + [
#     "ngrok-skip-browser-warning",
# ]


CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    # "http://localhost:5174",
    # "http://ec2-44-200-143-253.compute-1.amazonaws.com:86",
    "https://trench-probing-decimeter.ngrok-free.dev",
    "https://unaligned-faceted-gander.ngrok-free.dev"
    
    ]

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "http://ec2-44-200-143-253.compute-1.amazonaws.com:86",
    "https://trench-probing-decimeter.ngrok-free.dev",
    "https://unaligned-faceted-gander.ngrok-free.dev"
    ]

# Application definition

INSTALLED_APPS = [
    'daphne',
    'corsheaders',  # Add this
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
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
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
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }



# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'crm_demo_2',
# 		'USER': 'postgres',
#         'PASSWORD': 'Bharath@2004',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'crm_api',
		'USER': 'postgres',
        'PASSWORD': 'Siva@2002',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'

TIME_ZONE = 'Asia/Kolkata'  # ✅ IST
USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Authentication User model
AUTH_USER_MODEL = 'telecalling.User'



# Rest framework exception handler.
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'utils.exceptions.api_exception_handler',          #mithin_ecommerce_api.
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}


# SIMPLE JWT Configurations,
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

# Using the below configs directly for Access Token
ACCESS_TOKEN_GENERIC_LIFETIME = timedelta(days=1)       
# ACCESS_TOKEN_GENERIC_LIFETIME = timedelta(minutes=1)
# ACCESS_TOKEN_MOBILE_LIFETIME = timedelta(minutes=1)
ACCESS_TOKEN_MOBILE_LIFETIME = timedelta(days=30)

# huey
HUEY = {
    'name': 'crm',  # Use db name for huey.
    'result_store': True,  # Store return values of tasks.
    'events': True,  # Consumer emits events allowing real-time monitoring.
    'store_none': False,  # If a task returns None, do not save to results.
    'immediate': False,  # If DEBUG=True, run synchronously.
    'store_errors': True,  # Store error info if task throws exception.
    'blocking': False,  # Poll the queue rather than do blocking pop.
    'backend_class': 'huey.RedisHuey',  # Use path to redis huey by default,
    'connection': {
        'host': 'localhost',
        'port': 6379,
        'db': 1,
        'connection_pool': None,  # Definitely you should use pooling!
        # ... tons of other options, see redis-py for details.

        # huey-specific connection parameters.
        # 'read_timeout': 1,  # If not polling (blocking pop), use timeout.
        # 'max_errors': 1000,  # Only store the 1000 most recent errors.
        # 'url': None,  # Allow Redis config via a DSN.
    },
    'consumer': {
        'workers': 1,
        'worker_type': 'thread',
        'initial_delay': 0.1,  # Smallest polling interval, same as -d.
        'backoff': 1.15,  # Exponential backoff using this rate, -b.
        'max_delay': 10.0,  # Max possible polling interval, -m.
        'utc': False,  # Treat ETAs and schedules as UTC datetimes.
     
        'timezone': 'Asia/Kolkata', # IST timezone
        'scheduler_interval': 1,  # Check schedule every second, -s.
        'periodic': True,  # Enable crontab feature.
        'check_worker_health': True,  # Enable worker health checks.
        'health_check_interval': 1,  # Check worker health every second.
    },
    # These two lines make Huey run crontab jobs in IST
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
