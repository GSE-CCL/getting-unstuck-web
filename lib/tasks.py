from celery import Celery

def make_celery(name, backend, broker, app):
    """Make the Celery app. https://flask.palletsprojects.com/en/1.1.x/patterns/celery/
    
    Args:
        name (str): the name of the app.
        backend (str): the URI of the backend.
        broker (str): the URI of the broker.
        app (Flask.app): the Flask app we're adding the Celery instance to.

    Returns:
        An instance of celery.Celery.
    """

    celery = Celery(
        name,
        backend=backend,
        broker=broker
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
