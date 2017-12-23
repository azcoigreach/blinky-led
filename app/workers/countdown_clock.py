from multiprocessing import Process, Manager
import time
import datetime
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def countdown_clock():
    logger.warning('Initiate Countdown Clock')
    while True:
        dt = datetime.datetime
        count = dt(2021,1,21,9) - dt.now()
        d['count_down'] = '%dDays %dH %dM' % (count.days, count.seconds/3600, count.seconds%3600/60)
        
        logger.info('Count Clock: %s', d['count_down'])
        time.sleep(2)