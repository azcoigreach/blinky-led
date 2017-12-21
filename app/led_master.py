#!/usr/bin/env python 2.7
import time

from multiprocessing import Process, Lock, Manager, Value, Array
from multiprocessing.sharedctypes import Value, Array

import feedparser, bitly_api
import urllib2
import json
import os
import threading
from PIL import Image, ImageFont, ImageDraw
import random


from workers import *

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('MASTER')


def main():
    pass

if __name__ == "__main__":
    try:
        logger.warning('Work Started: PID %d', os.getpid())
        
        jobs = []
        lock = Lock()
        manager = Manager()
        
        #Process Variables
        time_now = manager.Array('c', b'88/88/88 88:88') 
        count_down = manager.Array('c', b'8888Days 88H 88M')
        curr_temp = manager.Value('d', 888.8)
        news_ticker = manager.Array('c', b'9999.ppm')
        news_ticker.value = str('0.ppm')
        ticker_ready = manager.Value('i', 0)
        curr_tweet = manager.Array('c', b'screen_name: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx : ddd mmm DD HH:MM:SS +0000 YYYY') 
     

        apps = [led_update.led_update, tweet_query.tweet_query, led_clock.led_clock, countdown_clock.countdown_clock, weather.weather] 
        processes = {}
        n=0
        for app in apps:
            instance = app()
            pprint.pprint(instance)
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
    