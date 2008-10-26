"""
Copyright (c) 2007-2008, Dj Gilcrease
All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import cPickle
from threading import Timer
from datetime import datetime

from apps.cron.signals import cron_done
from apps.cron import models

class AlreadyRegistered(Exception):
    pass

class Job(object):
    run_every = 86400

    def run(self, *args, **kwargs):
        cron_done.send(self)

class CronScheduler(object):
    def register(self, job, *args, **kwargs):
        """
            Register the given Job with the scheduler class
        """

        if not isinstance(job, Job):
            raise TypeError("You can only register a Job not a %r" % job)

        try:
            job = models.Job.objects.get(name__exact=str(job.__class__))
            job.args = cPickle.dumps(args)
            job.kwargs = cPickle.dumps(kwargs)
            job.save()
        except models.Job.DoesNotExist:
            job = models.Job(name=str(job.__class__), instance=cPickle.dumps(job()),
                        args=cPickle.dumps(args), kwargs=cPickle.dumps(kwargs),
                        last_executed=datetime.now(), queued=False)
            job.save()

    def execute(self):
        """
            Que all Jobs for execution
        """
        status = models.Cron.objects.get_or_create(pk=1)
        if status.executing:
            return

        status.executing = True
        status.save()

        jobs = models.Job.objects.all()
        for job in jobs:
            try:
                inst = cPickle.loads(job.instance)
                args = cPickle.loads(job.args)
                kwargs = cPickle.loads(job.kwargs)
                if not inst.queued:
                    Timer(inst.run_every, inst.run, args=args, kwargs=kwargs).start()
                    job.queued = True
                    job.instance = cPickle.dumps(inst)
                    job.save()
            except Exception:
                job.delete()

        status.executing = False
        status.save()

    def _requeue(self, sender, **kwargs):
        if not isinstance(sender, Job):
            raise TypeError("You can only requeue a Job not a %r" % sender)

        job = models.Job.objects.get(name__exact=str(sender.__class__))
        job.instance = cPickle.dumps(sender)
        job.queued = False
        job.save()


cron = CronScheduler()