from multiprocessing.sharedctypes import Value, Array
from time import strftime
import time
import datetime
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class led_clock():
    def __init__(self, *args, **kwargs):
        while True:
            dt = datetime.datetime
            t = dt.now()
            time_now.value = t.strftime('%m/%d/%y %H:%M')
            logger.debug('Current Time: %s',time_now.value)
            time.sleep(2)