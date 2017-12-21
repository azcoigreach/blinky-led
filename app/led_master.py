#!/usr/bin/env python 2.7
from time import strftime

__author__ =        "Stranger Production, LLC"
__created__ =       "23 January 2017"
__modified__ =      "21 December 2017"
__version__ =       "0.2.0"
__description___ =  '''MASTER LED CONTROL PROGRAM 
                    LED Board Project for Adafruit RGB-LED Hat 
                    with 2x 32x64px LED boards.'''
__changes__ =       ''' Version Changes
                    0.0.1 + Add LED Matrix Class and Default Template with variables to populate.
                          + led_clock module online in its own process and handing variables to
                          the main led_update loop.
                          +Added RSS Feed and BITLY ticker block
                    0.0.2 o Fixing Code for scroller and RSS
                    0.0.3 + Added now()+30minutes clock for RSS to Console
                          + Moved clock to bottom right
                          + Scrolling PPM ticker working - Need to move file open calls to slower process.
                          o Cleaned code
                    0.0.4 - Stop RSS feed
                          + Add Pushbullet feed
                    0.1.0 + Dockerized Application
                    0.2.0 + added mongodb connection
                    '''
                        
from blinkybase import BlinkyBase
from rgbmatrix import graphics
import time
from multiprocessing import Process, Lock
from multiprocessing.sharedctypes import Value, Array
import datetime
import feedparser, bitly_api
import urllib2
import json
import os
import threading
from PIL import Image, ImageFont, ImageDraw
import random
import logging
from pushbullet import Pushbullet
from pushbullet import Listener
from pymongo import MongoClient
import pprint
from workers import *

import led_update
# import workers.tweet_query
# import workers.led_clock
# import workers.countdown_clock
# import workers.rss_feed
# import workers.weather
# import workers.pb_query

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('led_master')


def main():
    pass

if __name__ == "__main__":
    try:
        logger.warning('Work Started: PID %d', os.getpid())
        
        jobs = []
        lock = Lock()
        
        
        #Process Variables
        time_now = Array('c', b'88/88/88 88:88' ,lock=lock) 
        count_down = Array('c', b'8888Days 88H 88M' ,lock=lock)
        curr_temp = Value('d', 888.8)
        news_ticker = Array('c', b'9999.ppm' ,lock=lock)
        news_ticker.value = str('0.ppm')
        ticker_ready = Value('i', 0)
        curr_tweet = Array('c', b'screen_name: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx : ddd mmm DD HH:MM:SS +0000 YYYY', lock=lock) 
     

        apps = ['workers.led_update','workers.tweet_query','workers.led_clock','workers.countdown_clock','workers.weather'] 
        processes = {}
        n=0
        for app in apps:
            instance = app()
            p = Process(target=instance.start_listener)
            p.start()
            processes[n] = (p, app) # Keep the process and the app to monitor or restart
            n += 1

        while len(processes) > 0:
            for n in processes.keys():
                (p, a) = processes[n]
                time.sleep(0.5)
                if p.exitcode is None and not p.is_alive(): # Not finished and not running
                    # Do your error handling and restarting here assigning the new process to processes[n]
                    logger.warning('is gone as if never born!',a)
                elif p.exitcode < 0:
                    logger.warning('Process Ended with an error or a terminate', a)
                    # Handle this either by restarting or delete the entry so it is removed from list as for else
                else:
                    logger.warning('finished', a)
                    p.join() # Allow tidyup
                    del processes[n] # Removed finished items from the dictionary 
                    # When none are left then loop will end
        
        
        # #Start TWEET_QUERY LOOP
        # rt = Process(target=tweet_query, name='tweet_query')
        # jobs.append(rt)
        # rt.start()

        # #Start LED_CLOCK LOOP
        # rt = Process(target=led_clock, name='led_clock')
        # jobs.append(rt)
        # rt.start()
        
        # #Start COUNTDOWN_CLOCK LOOP
        # rt = Process(target=countdown_clock, name='countdown_clock')
        # jobs.append(rt)
        # rt.start()
        
        # #Start WEATHER LOOP
        # rt = Process(target=weather, name='weather')
        # jobs.append(rt)
        # rt.start()
        
        # #Start RSS Feed Updater
        # # rt = Process(target=rss_feed)
        # # jobs.append(rt)
        # # rt.start()
        
        # #Start Pushbullet Listener
        # # rt = Process(target=pb_main)
        # # jobs.append(rt)
        # # rt.start()
        
        # #Start LED UPDATE LOOP
        # rt = Process(target=led_update, name='led_update')
        # jobs.append(rt)
        # rt.start()
        
        # #JOIN ALL JOBS
        # for j in jobs:
        #     j.join()
        #     logger.info(j)
            
    except KeyboardInterrupt:
        for j in jobs:
            j.terminate()
            time.sleep(2)
            logger.warning('Shutting Down: %s %s', j, j.is_alive())
    