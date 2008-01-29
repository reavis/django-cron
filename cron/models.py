from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, timedelta

class CronType(models.Model):
    app_label = models.CharField(max_length=255)
    name = models.CharField(max_length=255, unique=True)
    run_every = models.IntegerField(default=86400)
    cache_timeout = models.PositiveIntegerField(default=0)

    def for_class(cls, cron_class):
        return CronType.objects.get_or_create(
            app_label = cron_class.__module__.split('.')[-2],
            name = cron_class.__name__,
            run_every = cron_class.run_every
        )[0]
    for_class = classmethod(for_class)

    def __unicode__(self):
        return u'%s.%s' % (self.app_label, self.name)

class Cron(models.Model):
    type = models.ForeignKey(CronType)
    next_run = models.DateTimeField(default=datetime.now())

    def run(self):
        self.next_run = self.next_run + timedelta(seconds=self.type.run_every)
        self.save()

    class Meta:
        pass