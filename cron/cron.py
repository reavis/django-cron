from datetime import datetime
from django.contrib.sessions.models import Session
import apps.cron

class DeleteSessions(apps.cron.Cron):
    run_every = 24

    def job(self):
        now = datetime.now()
        try:
            Session.objects.filter(expire_date__lt=now).delete()
            return True
        except:
            return False
