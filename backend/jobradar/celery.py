"""Week 2: the Celery app. Redis is the broker (task queue) and the result backend.

Run from the backend folder (Redis must be running):
    celery -A jobradar worker -l info --pool=solo      (--pool=solo is needed on Windows)
    celery -A jobradar beat -l info

TODO Week 2: uncomment, then uncomment the import in jobradar/__init__.py
and the CELERY_ settings in settings.py.

    import os
    from celery import Celery

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jobradar.settings")

    app = Celery("jobradar")
    app.config_from_object("django.conf:settings", namespace="CELERY")
    app.autodiscover_tasks()   # finds tasks.py in every installed app

Interview topics: broker vs result backend, worker vs beat, what happens to a
task if the worker crashes in the middle (acks_late), why tasks must be idempotent.
"""
