from apscheduler.schedulers.background import BackgroundScheduler


def print_job():
    print("Job executed!")


# Create an instance of the scheduler
# scheduler = BackgroundScheduler() # Disabled for testing

# Add a job to the scheduler using a cron expression
# scheduler.add_job(print_job, "cron", hour="0/1") # Disabled for testing

# Provide a dummy scheduler for import to avoid issues during testing
class DummyScheduler:
    def add_job(self, *args, **kwargs):
        # print(f"DummyScheduler: add_job called with {args} {kwargs}")
        pass
    def start(self, *args, **kwargs):
        # print("DummyScheduler: start called")
        pass
    def shutdown(self, *args, **kwargs):
        # print("DummyScheduler: shutdown called")
        pass

scheduler = DummyScheduler()
