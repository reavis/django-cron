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

from django.dispatch import dispatcher
from signals import cron_done
import models
import sqlite3

try:
	# Delete all the old jobs from the database so they don't interfere with this instance of django
	oldJobs = models.Job.objects.all()
	for oldJob in oldJobs:
		oldJob.delete()
except sqlite3.OperationalError:
	# When you do syncdb for the first time, the table isn't 
	# there yet and throws a nasty error... until now
	pass

class AlreadyRegistered(Exception):
	pass

class Job(object):
	run_every = 86400

	def run(self, *args, **kwargs):  
		self.job()
		cron_done.send(sender=self, *args, **kwargs)
		
	def job(self):
		"""
		Should be overridden (this way is cleaner, but the old way - overriding run() - will still work)
		"""
		pass

class CronScheduler(object):
	def register(self, job, *args, **kwargs):
		"""
			Register the given Job with the scheduler class
		"""
		
		job = job()
		
		if not isinstance(job, Job):
			raise TypeError("You can only register a Job not a %r" % job)

		try:
			job = models.Job.objects.get(name__exact=str(job.__class__))
			job.args = cPickle.dumps(args)
			job.kwargs = cPickle.dumps(kwargs)
			job.save()
		except models.Job.DoesNotExist:
			job = models.Job(
						name=str(job.__class__), 
						instance=cPickle.dumps(job),
						args=cPickle.dumps(args), 
						kwargs=cPickle.dumps(kwargs),
			)
			job.save()

	def execute(self):
		"""
			Que all Jobs for execution
		"""
		status = models.Cron.objects.get_or_create(pk=1)[0]
		if status.executing:
			return

		status.executing = True
		status.save()

		jobs = models.Job.objects.all()
		for job in jobs:
			try:
				inst = cPickle.loads(str(job.instance))
				args = cPickle.loads(str(job.args))
				kwargs = cPickle.loads(str(job.kwargs))
				if not job.queued:
					Timer(inst.run_every, inst.run, *args, **kwargs).start()
					job.queued = True
					job.save()
			except Exception:
				job.delete()

		status.executing = False
		status.save()

def RequeueJob(*args, **kwargs):
	sender = kwargs['sender']
	
	if not isinstance(sender, Job):
		raise TypeError("You can only requeue a Job not a %r" % sender)

	job = models.Job.objects.get(name__exact=str(sender.__class__))
	job.instance = cPickle.dumps(sender)
	job.queued = False
	job.save()
	cron.execute()

cron = CronScheduler()
cron_done.connect(RequeueJob)
  