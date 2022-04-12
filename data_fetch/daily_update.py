from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from nytimes_crawler import start_nytimes_crawling
from bbc_crawler import start_bbc_crawling
from generate_configs import updateNyTimesCFG
from generate_configs import updateBBCCFG
import sys
sys.path.append("..")
from pipeline import pipeline, get_index

# update scripts
def runScript():
    
    # update configs -- time
    updateNyTimesCFG()
    updateBBCCFG()
    
    # craw news
    start_nytimes_crawling("settings/nytimes_update.cfg")
    start_bbc_crawling("settings/bbc_update.cfg")
    
    # start pipeline
    pipeline("daily_news/nytimes", 1)
    pipeline("daily_news/bbc", 2)

    
    
    

 
if __name__ == '__main__':
    
    # create background scheduler
    #scheduler = BackgroundScheduler()
    scheduler = BlockingScheduler()
    
    # add jobs -- interval or cron
    # interval -- triggered after certain time
    # cron     -- triggered at a specific time
    
    # scheduler.add_job(runScript, 'interval', seconds=30, id = 'test_job')
    # triggered on 23:00 everyday
    scheduler.add_job(runScript, 'cron', hour='23', minute='00')
    
    # start scheduler
    scheduler.start()
