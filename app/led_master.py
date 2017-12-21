#!/usr/bin/env python 2.7
import time
from multiprocessing import Process, Manager
import os
from workers import *
import logging
logging.basicConfig(level=logging.debug)
logger = logging.getLogger('MASTER')

if __name__ == "__main__":
    try:
        logger.warning('Work Started: PID %d', os.getpid())
        manager = Manager()
        d = manager.dict()
        d={'time_now': b'88/88/88 88:88', 'count_down': b'8888Days 88H 88M', 'curr_temp':888.8, 'news_ticker':b'0.ppm', 'curr_tweet':b'screen_name: xxxx : ddd mmm DD HH:MM:SS +0000 YYYY'}
        logger.debug(d)
        apps = [led_update.led_update, tweet_query.tweet_query, led_clock.led_clock, countdown_clock.countdown_clock, weather.weather] 
        processes = {}
        n=0
        while True:
            for app in apps:
                instance = app(d)
                pprint.pprint(instance)
                p = Process(target=instance.start_listener, args=(d,))
                p.start()
                processes[n] = (p, app)
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
        
            
    except KeyboardInterrupt:
        for n in processes.keys():
            (p, a) = processes[n]
            p.terminate()
            time.sleep(2)
            logger.warning('Shutting Down: %s %s', p, p.is_alive())
    