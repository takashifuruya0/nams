from nams.settings import *

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "nams",
        "USER": "temp",  #env('FKMANAGE_DB_USER'),
        "PASSWORD": "temp",  #env('FKMANAGE_DB_PASSWORD'),
        'HOST': "temp",  #env("FKMANAGE_DB_HOST"),
        "POST": "",
        "ATOMIC_REQUESTS": True,
    }
}
# update db settings
db_from_env = dj_database_url.config(conn_max_age=400)
DATABASES['default'].update(db_from_env)

# Debug
DEBUG = False

# ENVIRONMENT
ENVIRONMENT = "production"

# LOG

LOGGING['handlers'] = {
    'logfile': {
        'level': 'INFO',
        'class': 'logging.FileHandler',
        'formatter': 'verbose',
        'filename': "/var/log/gunicorn/nams_logfile",
    },
    'elogfile': {
        'level': 'ERROR',
        'class': 'logging.FileHandler',
        'formatter': 'verbose',
        'filename': "/var/log/gunicorn/nams_elogfile",
    },
}

LOGGING['loggers'] = {
    'django': {
        'handlers': ['logfile', 'elogfile'],
        'level': 'INFO',
    },
}

