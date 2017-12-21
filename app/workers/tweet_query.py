from multiprocessing import Process, Manager
from pymongo import MongoClient
import pprint
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class tweet_query(self,d):
    def __init__(self, *args, **kwargs):
        global d
        client = MongoClient('192.168.1.240', 27017)
        db = client.twitter_stream
        logger.warning('tweet_query started')
        while True:
            try:
                query = { '$query' : {}, '$orderby' : { '$natural' : -1 } }
                projection = { '_id' : 0, 'user.screen_name' : 1, 'text' : 1 ,'created_at' : 1}
                result = db.twitter_query.find_one(query, projection)
                self.output = str(result['user']['screen_name'] + ': ' + result['text'] + ': ' + result['created_at']).encode('ascii','ignore')
                logger.info('Tweet: %s', self.output)
                d['curr_tweet'] = self.output
            except Exception as err:
                logger.error('Tweet Query Error: %s', err)
                time.sleep(10)
                tweet_query()
            time.sleep(30)
