import time
from multiprocessing import Process, Manager
from pymongo import MongoClient
import pprint
import pickle
import string
from datetime import datetime
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



class tweet_query():
    def __init__(self, *args, **kwargs):
        logger.warning('Init: Tweet Query')
        try: 
            client = MongoClient('192.168.1.240', 27017)
            db = client.twitter_stream
            logger.warning('tweet_query started')
        except Exception as err:
            logger.error('Database connection Error: %s', err)
        twitter = {'curr_tweet': ''}
        while True:
            try:
                query = { '$query' : {}, '$orderby' : { '$natural' : -1 } }
                projection = { '_id' : 0, 'user.screen_name' : 1, 'text' : 1 ,'created_at' : 1}
                result = db.twitter_query.find_one(query, projection)
                logger.debug(result)

                printable = set(string.printable)
                text_filter = filter(lambda x: x in printable, result['text'])
                tweet_iso_date = result['created_at']
                tweet_date = datetime.tweet_iso_date.strftime('%a %b %d %H:%M:%S +0000 %Y')
                output = str(result['user']['screen_name'] + ': ' + text_filter + ': ' + tweet_date).encode('ascii', errors='ignore')
                
                logger.debug('Twitter String Output: %s', output)
                twitter = {'curr_tweet': output}
                logger.info('Tweet: %s', twitter['curr_tweet'])
                pickle.dump(twitter, open('twitter.pickle', 'wb'))
                
            except Exception as err:
                logger.error('Tweet Query Error: %s', err)
                twitter = {'curr_tweet': 'no data'}
                pickle.dump(twitter, open('twitter.pickle', 'wb'))
                logger.info('Tweet: %s', twitter['curr_tweet'])
                time.sleep(10)
                continue
            time.sleep(30)

class tweet_hashtags():
    def __init__(self, *args, **kwargs):
        logger.warning('Init: Tweet Hashtags')
        try: 
            client = MongoClient('192.168.1.240', 27017)
            db = client.twitter_stream
            logger.warning('tweet_query started')
        except Exception as err:
            logger.error('Database connection Error: %s', err)
        twitter = {'curr_tweet': ''}
        while True:
            try:
                query = { '$query' : {}, '$orderby' : { '$natural' : -1 } }
                projection = { '_id' : 0, 'user.screen_name' : 1, 'text' : 1 ,'created_at' : 1}
                result = db.twitter_query.find_one(query, projection)
                logger.debug(result)
                printable = set(string.printable)
                text_filter = filter(lambda x: x in printable, result['text'])
                tweet_date = datetime.result['created_at'].strftime('%a %b %d %H:%M:%S +0000 %Y')
                output = str(result['user']['screen_name'] + ': ' + text_filter + ': ' + tweet_date).encode('ascii', errors='ignore')
                
                logger.debug('Twitter String Output: %s', output)
                twitter = {'curr_tweet': output}
                logger.info('Tweet: %s', twitter['curr_tweet'])
                pickle.dump(twitter, open('twitter.pickle', 'wb'))
                
            except Exception as err:
                logger.error('Tweet Query Error: %s', err)
                twitter = {'curr_tweet': 'no data'}
                pickle.dump(twitter, open('twitter.pickle', 'wb'))
                logger.info('Tweet: %s', twitter['curr_tweet'])
                time.sleep(10)
                continue
            time.sleep(30)    
