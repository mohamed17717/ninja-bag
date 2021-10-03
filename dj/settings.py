import os
from .local_settings import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '$e5rh03te^#or+2dvix(9zgnp0*xjya92e3guwni)r30p73x4-'

DEBUG = False

ALLOWED_HOSTS = [
  'ninja-bag.site'
]

INSTALLED_APPS = [
  'django.contrib.admin',
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.messages',
  'django.contrib.staticfiles',

  # apps
  'app',
  'toolsframe',
  'accounts',
  'tools',

  # third parties
  'django_user_agents',
  'crispy_forms',
  'corsheaders',
  'social_django',
  'debug_toolbar',
]

MIDDLEWARE = [
  'django.middleware.security.SecurityMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'corsheaders.middleware.CorsMiddleware',
  'django.middleware.common.CommonMiddleware',
  # 'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  'django.middleware.clickjacking.XFrameOptionsMiddleware',
  'django_user_agents.middleware.UserAgentMiddleware',

  'social_django.middleware.SocialAuthExceptionMiddleware',
  'app.middleware.WebRequestMiddleware',
  'app.middleware.RequestBodyToDataMiddleware',
  'debug_toolbar.middleware.DebugToolbarMiddleware'
]

ROOT_URLCONF = 'dj.urls'

TEMPLATES = [
  {
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(BASE_DIR, 'templates')],
    'APP_DIRS': True,
    'OPTIONS': {
      'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',

        'social_django.context_processors.backends',
        'social_django.context_processors.login_redirect',
      ],
    },
  },
]

WSGI_APPLICATION = 'dj.wsgi.application'

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
  }
}

AUTH_PASSWORD_VALIDATORS = [
  {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
  {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
  {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
  {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

USER_AGENTS_CACHE = 'default'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
VENV_PATH = os.path.dirname(BASE_DIR)
STATIC_ROOT = os.path.join(VENV_PATH, 'static')
MEDIA_ROOT = os.path.join(VENV_PATH, 'media')

# social auth configuration
AUTHENTICATION_BACKENDS = (
  'social_core.backends.github.GithubOAuth2',
  'social_core.backends.google.GoogleOAuth2',
  'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL = LOGIN_ERROR_URL = '/account/'
LOGIN_REDIRECT_URL = LOGOUT_REDIRECT_URL = '/'
SOCIAL_AUTH_URL_NAMESPACE = 'social'

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',

    'accounts.signals.get_avatar',
)

# cors
CORS_ALLOW_ALL_ORIGINS = True

# django debug toolbar setup
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
INTERNAL_IPS = ['127.0.0.1']

# caching
CACHES = {
  'default': {
    'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
    'LOCATION': '/var/tmp/django_cache',

    # 'TIMEOUT': 60,
    'OPTIONS': {
      'MAX_ENTRIES': 1000
    }
  }
}

if DEBUG:
  ALLOWED_HOSTS.append('127.0.0.1')

