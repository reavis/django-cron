How to install:

1. Put 'django_cron' into your python path
2. Add 'django_cron' to INSTALLED_APPS in your settings.py file
3. Add the following code to the beginning of your urls.py file (just after the imports):

import django_cron
django_cron.autodiscover()

4. Create a file called 'cron.py' inside each installed app that you want to add a recurring job to. The app must be installed via the INSTALLED_APPS in your settings.py or the autodiscover will not find it.

Here is an example cron.py:
--------------------------------------------------------------------
from django_cron.base import cron, Job

# This is a function I wrote to check a feedback email address and add it to our database. Replace with your own imports
from MyMailFunctions import check_feedback_mailbox

class CheckMail(Job):
	"""
		Cron Job that checks the lgr users mailbox and adds any approved senders' attachments to the db
	"""

	# run every 360 seconds (5 minutes)
	run_every = 360
		
	def job(self):
		# This will be executed every 5 minutes
		check_feedback_mailbox()

cron.register(CheckMail)

