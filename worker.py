from celery import Celery
 
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['result_backend'],
        broker=app.config['CELERY_BROKER_URL'],
        timezone='Asia/Kolkata',
        broker_connection_retry_on_startup = True
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                print("|--------------------|")
                print("Commencing New Task")
                print("|--------------------|")
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery