from multiprocessing import Process, Manager
from time import strftime
import time
import datetime
import logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class led_clock(d):
    def __init__(self, *args, **kwargs):
        logger.debug(d)
        while True:
            dt = datetime.datetime
            t = dt.now()
            d['time_now'] = t.strftime('%m/%d/%y %H:%M')
            logger.debug('Current Time: %s',d['time_now'])
            time.sleep(2)