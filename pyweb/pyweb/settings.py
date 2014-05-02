"""
Django settings for pyweb project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
PROJECT_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(PROJECT_DIR)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'k6jv9w9-ds%f)=r-!0zuu6-9&5poqq41ksw44j-1^snc)t*nf4'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'chat',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'pyweb.urls'

WSGI_APPLICATION = 'pyweb.wsgi.application'


# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
	os.path.join(PROJECT_DIR, 'static'),
)


# Template Directories
TEMPLATE_DIRS = (
	os.path.join(PROJECT_DIR, 'templates'),
)

# Logging Configuration
if DEBUG:
	LOGGING = {
		'version' : 1,
		'disable_existing_loggers' : False,
		'formatters' : {
			'simple' : {
				'format' : '%(asctime)s %(levelname)s %(message)s',
			}
		},
		'handlers' : {
			'console' : {
				'level' : 'DEBUG',
				'class' : 'logging.StreamHandler',
				'formatter' : 'simple',
			}
		},
		'root' : {
			'level' : 'INFO',
			'handlers' : ['console',],
		},
		'loggers' : {
			'django.request' : {
				'handlers' : False,
				'level' : 'DEBUG',
			},
		},
	}
