env need: database url sync+async, refresh and access tokens expires, hash algorithm, secret key
Redis docker run -p 6379:6379 redis
uviron main:app --reload
celery -A celery_app beat --loglevel=info
celery -A celery_app worker --loglevel=info --pool=solo