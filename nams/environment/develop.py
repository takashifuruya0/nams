from nams.settings import *

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "nams_dev",
        "USER": env('FKMANAGE_DB_USER'),
        "PASSWORD": env('FKMANAGE_DB_PASSWORD'),
        'HOST': env("FKMANAGE_DB_HOST"),
        "POST": "",
        "ATOMIC_REQUESTS": True,
    }
}
# update db settings
db_from_env = dj_database_url.config(conn_max_age=400)
DATABASES['default'].update(db_from_env)

# Debug
DEBUG = True

# ENVIRONMENT
ENVIRONMENT = "develop"
