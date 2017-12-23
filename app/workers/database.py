from multiprocessing import Process, Manager
from pymongo import MongoClient
import pprint
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)



class database():
    def __init__(self, *args, **kwargs):
        # logger.warning('init blinky db')
        
        # client = MongoClient('192.168.1.240', 27017)
        # db = client.blinky
        # logger.warning('connected to blink db')
        # while True:
        #     try:
        #         pass
               
        #     except Exception as err:
        #         logger.error('Dabase Error: %s', err)
                
                
        #     time.sleep(30)
        pass