import asyncio

from apscheduler.schedulers.blocking import BlockingScheduler

from daily_runner import run_daily_newsletter


scheduler = BlockingScheduler()


def run_newsletter():

    print("\nStarting scheduled newsletter run...")

    asyncio.run(
        run_daily_newsletter()
    )


# Run every day at 8:00 AM
scheduler.add_job(
    run_newsletter,
    "interval",
    minutes=1
)


print("AI Daily scheduler started.")
print("Newsletter will run every day at 08:00.")

try:

    scheduler.start()

except (KeyboardInterrupt, SystemExit):

    print("Scheduler stopped.")