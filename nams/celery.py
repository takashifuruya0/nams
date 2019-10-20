import os
from celery import Celery
import environ
env = environ.Env(DEBUG=(bool, False),)  # set default values and casting
environ.Env.read_env('.env')  # reading .env file

# set the default Django settings module for the 'celery' program.
settings = os.getenv(
   "DJANGO_SETTINGS_MODULE", env("CELERY_ENVIRONMENT"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)

app = Celery('nams')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(['namsw'])
