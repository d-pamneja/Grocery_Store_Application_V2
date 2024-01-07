web: gunicorn app:app
worker: celery -A app.celery_worker.celery worker --loglevel=info
beat: celery -A app.celery_worker.celery beat --loglevel=info