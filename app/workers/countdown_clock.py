from multiprocessing import Process, Lock, Manager
from multiprocessing.sharedctypes import Value, Array
import time
import datetime
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

class countdown_clock():
    def __init__(self, *args, **kwargs):
        logger.debug(d)
        while True:
            dt = datetime.datetime
            count = dt(2021,1,21,9) - dt.now()
            count_down.value = '%dDays %dH %dM' % (count.days, count.seconds/3600, count.seconds%3600/60)
            logger.debug('Count Clock: %s', count_down.value)
            time.sleep(2)