from apscheduler.schedulers.background import BackgroundScheduler


def print_job():
    print("Job executed!")


# Create an instance of the scheduler
scheduler = BackgroundScheduler()

# Add a job to the scheduler using a cron expression
scheduler.add_job(print_job, "cron", hour="0/1")
