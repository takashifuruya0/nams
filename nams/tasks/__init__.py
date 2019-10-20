# fmanage/tasks/__init__.py
from ..celery import app
# celery -A nams worker -c 2 -l info


@app.task()
def minus_numbers(a, b):
    print('Request: {}-{}={}'.format(a, b, a - b))
    return a - b


@app.task()
def add_numbers(a, b):
    print('Request: {}+{}={}'.format(a, b, a + b))
    return a + b



