from apps.cron import Cron


def cron_jobs(request):
    ret = Cron.run_cron()
    return ret