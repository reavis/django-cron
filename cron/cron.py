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
from datetime import datetime

from django.contrib.sessions.models import Session

from cron import cron, Job, models

class Execute(Job):
    """
        Cron Job that will ensure that all jobs are checked every 60 seconds
    """
    run_every = 60

    def run(self, *args, **kwargs):
        cron.execute()
        super(Execute, self).run()

class DeleteSessions(Job):
    """
        Cron Job that deletes expired Sessions
    """
    run_every = 86400

    def run(self, *args, **kwargs):
        Session.objects.filter(expire_date__lt=datetime.now()).delete()
        super(Execute, self).run()

cron.register(Execute)
cron.register(DeleteSessions)


# This is here only to get the Cron Jobs started running
# Do not include this in your own Jobs
cron.execute()