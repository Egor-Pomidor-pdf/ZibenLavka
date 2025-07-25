import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ziben.settings")

app = Celery("ziben")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.timezone = "UTC"
app.conf.beat_schedule = {
    "every-minute-task": {
        "task": "game.tasks.update_shop",
        "schedule": 25,
    },
}
