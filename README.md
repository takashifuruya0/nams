# Overview
NAMS; New Asset Management System
Started creating the system since 13rd Oct., 2019
Created by tfhand

## Running locally
```
cd nams
sudo docker run -d -p 6379:6379 redis
celery -A nams worker -c 2 -l info &
python3 manage.py runserver_plus
```


