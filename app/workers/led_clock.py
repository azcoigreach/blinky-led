from multiprocessing import Process, Manager, Queue
from time import strftime
import time
import datetime
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def led_clock():

    
    logger.warning('Init Clock')
    while True:
        dt = datetime.datetime
        dt_now = dt.now().strftime('%m/%d/%y %H:%M')
        d['time_now'] = str(dt_now)
        logger.info('Current Time: %s',d['time_now'])
        
        time.sleep(2)
