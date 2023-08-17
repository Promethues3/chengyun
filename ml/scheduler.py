from task import main
from apscheduler.schedulers.blocking import BlockingScheduler

if __name__ == '__main__':
    # 创建后台执行的
    main()
    scheduler = BlockingScheduler()
    scheduler.add_job(func=main, trigger="interval", days="1")
    scheduler.start()