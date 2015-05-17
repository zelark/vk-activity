from apscheduler.schedulers.blocking import BlockingScheduler
from subprocess import call


sched = BlockingScheduler()

@sched.scheduled_job('interval', seconds=60)
def timed_job():
    call(['python', 'vk_activity.py'])

def run_rest_server():
    call(['python', 'rest-server.py'])

rest_job = sched.add_job(run_rest_server)

sched.start()
