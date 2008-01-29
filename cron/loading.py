from django.conf import settings

class CronCache(object):
    def __init__(self):
        self.discovered = False
        self.crons = {}

    def register(self, name, module):
        """
        Register the cron in cache for later use.
        """
        if name in self.crons:
            raise KeyError, "Only one cron named %s can be registered." % name

        self.crons[name] = module

    def discover_crons(self):
        if self.discovered:
            return
        for app in settings.INSTALLED_APPS:
            # Just loading the module will do the trick
            __import__(app, {}, {}, ['cron'])
        self.discovered = True

    def get_all_crons(self):
        self.discover_crons()
        return self.crons.values()

registry = CronCache()
