import asyncio

from apscheduler.schedulers.blocking import BlockingScheduler

from daily_runner import run_daily_newsletter


scheduler = BlockingScheduler(
    timezone="Asia/Kolkata"
)


def run_newsletter():
    print("\n" + "=" * 80)
    print("STARTING SCHEDULED NEWSLETTER RUN")
    print("=" * 80)

    try:
        asyncio.run(run_daily_newsletter())

        print("\n" + "=" * 80)
        print("SCHEDULED NEWSLETTER COMPLETED")
        print("=" * 80)

    except Exception as e:
        print("\n" + "=" * 80)
        print("SCHEDULED NEWSLETTER FAILED")
        print("=" * 80)
        print(f"Error: {e}")


scheduler.add_job(
    run_newsletter,
    "cron",
    hour=21,
    minute=30,
    id="daily_ai_newsletter",
    replace_existing=True
)


print("=" * 80)
print("AI DAILY NEWSLETTER SCHEDULER")
print("=" * 80)
print("Scheduler started successfully.")
print("Newsletter schedule: Every day at 09:00 PM IST")
print("=" * 80)


try:
    scheduler.start()

except (KeyboardInterrupt, SystemExit):
    print("\nScheduler stopped.")