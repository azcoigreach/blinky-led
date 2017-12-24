#!/usr/bin/env python 2.7
from time import strftime
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
import pickle
from workers import *
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('MASTER')
logger.setLevel(logging.INFO)

class RunText(BlinkyBase):
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        logger.warning('Init: LED Loop')

    def Run(self):
        
        
        offscreenCanvas = self.matrix.CreateFrameCanvas()
        
        #Format
        time_font = graphics.Font()
        time_font.LoadFont("/home/pi/led/fonts/4x6.bdf")
        time_color = graphics.Color(157, 31, 186)
        
        count_font = graphics.Font()
        count_font.LoadFont("/home/pi/led/fonts/4x6.bdf")
        count_color = graphics.Color(198, 29, 41)
        
        line_a_color = graphics.Color(27, 93, 198)
        
        count_label_font = graphics.Font()
        count_label_font.LoadFont("/home/pi/led/fonts/4x6.bdf")
        count_label_color = graphics.Color(198, 29, 41)
        
        count_wx_font = graphics.Font()
        count_wx_font.LoadFont("/home/pi/led/fonts/4x6.bdf")
        count_wx_color = graphics.Color(204, 171, 40)
        
        ticker_font = graphics.Font()
        ticker_font.LoadFont("/home/pi/led/fonts/8x13.bdf")
        ticker_color = graphics.Color(99, 127, 115)
        self.pos = offscreenCanvas.width
        
        led_width = offscreenCanvas.width
        
        self.curr_temp = ''
        self.curr_tweet = ''

        while True:

            try:
                self.weather = pickle.load(open('weather.pickle', 'rb'))
                logger.debug('Weather Pickle: %s', self.weather)
                self.curr_temp = self.weather['curr_temp']

                self.twitter = pickle.load(open('twitter.pickle', 'rb'))
                logger.debug('Twitter Pickle: %s', self.twitter)
                self.curr_tweet = self.twitter["curr_tweet"]

            except Exception as err:
                logger.error('Pickle Error: %s', err)
                

            offscreenCanvas.Clear()
            self.clock = time_now.value
            self.count_down = count_down.value
            graphics.DrawText(offscreenCanvas, count_font, 1, 31, count_color, self.count_down)
            graphics.DrawLine(offscreenCanvas, 0, 18, 128, 18, line_a_color)
            graphics.DrawLine(offscreenCanvas, 68, 19, 68, 32, line_a_color)
            graphics.DrawText(offscreenCanvas, time_font, 71, 31, time_color, self.clock)
            graphics.DrawText(offscreenCanvas, count_label_font, 1, 25, count_label_color, 'NOT MY PRESIDENT!')
            graphics.DrawText(offscreenCanvas, count_wx_font, 104, 25, count_wx_color, self.curr_temp)
            
            # Top Twitter Ticker
        
            len = graphics.DrawText(offscreenCanvas, ticker_font, self.pos, 14, ticker_color, self.curr_tweet)
            self.pos -= 1
            if (self.pos + len < 0):
                self.pos = offscreenCanvas.width
            
            time.sleep(0.025)
            offscreenCanvas = self.matrix.SwapOnVSync(offscreenCanvas)

def led_update():
    parser = RunText()
    if (not parser.process()):
        parser.print_help()
        

class led_clock():
    def __init__(self, *args, **kwargs):
        while True:
            dt = datetime.datetime
            t = dt.now()
            time_now.value = t.strftime('%m/%d/%y %H:%M')
            #print(time_now.value)
            time.sleep(5)


class countdown_clock():
    def __init__(self, *args, **kwargs):
        while True:
            dt = datetime.datetime
            count = dt(2021,1,21,9) - dt.now()
            count_down.value = '%dDays %dH %dM' % (count.days, count.seconds/3600, count.seconds%3600/60)
            #print(count_down.value)
            time.sleep(5)
    
            
def main():
    pass

if __name__ == "__main__":
    try:
        logger.warning('Work Started: PID %d', os.getpid())
        with Manager() as manager:
            d = manager.dict()
            d = {'time_now': b'88/88/88 88:88', 'count_down': b'8888Days 88H 88M', 'curr_temp':888.8, 'news_ticker':b'0.ppm', 'curr_tweet':b'screen_name: xxxx : ddd mmm DD HH:MM:SS +0000 YYYY'}
            logger.debug(d)
            apps = [led_update.RunText] #, tweet_query.tweet_query, led_clock.led_clock, countdown_clock.countdown_clock, weather.weather] 
            processes = {}
            n=0
            for app in apps:
                instance = app(d)
                p = Process(target=instance, args=(d,))
                p.start()
                processes[n] = (p, app)
                n += 1
                logger.warning('Procs Started: %s ', p, p.is_alive())
                time.sleep(0.25)

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
        
        #Start LED_CLOCK LOOP
        rt = Process(target=countdown_clock)
        jobs.append(rt)
        rt.start()
                
        #Start LED UPDATE LOOP
        rt = Process(target=led_update)
        jobs.append(rt)
        rt.start()
        
        #JOIN ALL JOBS
        for j in jobs:
            j.join()
            print(j)
            
    except KeyboardInterrupt:
        for j in jobs:
            j.terminate()
            time.sleep(2)
            print(j, j.is_alive())
    