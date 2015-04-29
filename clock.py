from apscheduler.schedulers.blocking import BlockingScheduler
from subprocess import call


sched = BlockingScheduler()

@sched.scheduled_job('interval', seconds=60)
def timed_job():
    call(['python', 'heartbeat.py'])

sched.start()
