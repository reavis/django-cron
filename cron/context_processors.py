from apps.cron import Cron


def cron_jobs(request):
    #Dont bother processing the cron check if this user has already done so this session
    if request.session.get('cron_done', False):
        return {}

    ret = Cron.run_cron()
    request.session['cron_done'] = True

    return ret