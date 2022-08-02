from __future__ import absolute_import
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'affiliate.settings')
app = Celery('affiliate')
app.conf.enable_utc = False
app.conf.update(timezone = 'UTC')

app.conf.beat_schedule = {
    'get user followers from instagram,twitter,youtube and tiktok':{
        'task': 'accounts.user_socials',
        'schedule': crontab(hour=1, minute=10)
    }
}
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))