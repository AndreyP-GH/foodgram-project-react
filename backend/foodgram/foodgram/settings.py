# import os
from pathlib import Path

# from dotenv import load_dotenv

# load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-9u*!3czn4)ci^7hh!6+b%#!4z9d)w$i25$1wh^ih^28%kpzyj9'  # потом спрятать в str(os.getenv('SECRET_KEY'))

DEBUG = True

# на втором этапе заменить на
# '158.160.61.6',
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '[::1]',
    'testserver',
]

# на втором этапе добавить corsheaders' + pip install django-cors-headers && pip freeze > requirements.txt
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api.apps.ApiConfig',
    'recipes.apps.RecipesConfig',
    'users.apps.UsersConfig',
    'sorl.thumbnail',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'django_filters',
]

# на втором этапе добавить 'corsheaders.middleware.CorsMiddleware'
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'foodgram.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'foodgram.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# на втором этапе заменить на postgresql
# DATABASES = {
#     'default': {
#         'ENGINE': os.getenv('ENGINE',
#                             default='django.db.backends.postgresql'),
#         'NAME': os.getenv('DB_NAME'),
#         'USER': os.getenv('POSTGRES_USER'),
#         'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
#         'HOST': os.getenv('DB_HOST'),
#         'PORT': os.getenv('DB_PORT')
#     }
# }

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

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],

    'DEFAULT_PAGINATION_CLASS': 'api.pagination.CustomPagination',
    'PAGE_SIZE': 6,
}

DJOSER = {
    'LOGIN_FIELD': 'email',
    'SERIALIZERS': {
        'user': 'api.serializers.CustomUserSerializer',
        'current_user': 'api.serializers.CurrentUserSerializer',
        'set_password': 'djoser.serializers.SetPasswordSerializer',
        'user_create': 'api.serializers.RegistrationSerializer',
        'token': 'djoser.serializers.TokenSerializer',
        'token_create': 'djoser.serializers.TokenCreateSerializer',
    },
    'PERMISSIONS': {
        'user': ['rest_framework.permissions.AllowAny'],
        'user_create': ['rest_framework.permissions.AllowAny'],
        'user_list': ['rest_framework.permissions.AllowAny'],
        'set_password': ['api.permissions.IsAuthorOrReadOnly'],
        'token_create': ['rest_framework.permissions.AllowAny'],
        'token_destroy': ['api.permissions.IsAuthorOrReadOnly'],
    },
    'HIDE_USERS': False,
}

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True  # если ошибка по naive datetime, меняем на False

STATIC_URL = '/static/'
STATIC_ROOT = (BASE_DIR / 'static')
# STATICFILES_DIRS = ((BASE_DIR / 'static/'),)

MEDIA_URL = '/media/'
MEDIA_ROOT = (BASE_DIR / 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

# на втором этапе добавить
# CORS_ORIGIN_ALLOW_ALL = True

# CORS_URLS_REGEX = r'^/api/.*$'

FILE_NAME = 'Список_покупок.txt'