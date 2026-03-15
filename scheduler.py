from apscheduler.schedulers.blocking import BlockingScheduler
from models import init_db
from tracker import check_all_items
from home_tracker import check_all_home_searches


def run_all():
    # check_all_items()  # uncomment to enable eBay/Amazon tracking
    check_all_home_searches()


if __name__ == "__main__":
    init_db()
    print("[Scheduler] Starting — checking once a week.")
    run_all()  # run immediately on start

    scheduler = BlockingScheduler()
    scheduler.add_job(run_all, "interval", weeks=1)
    scheduler.start()
