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
        time_font.LoadFont("./fonts/4x6.bdf")
        time_color = graphics.Color(157, 31, 186)
        
        count_font = graphics.Font()
        count_font.LoadFont("./fonts/4x6.bdf")
        count_color = graphics.Color(198, 29, 41)
        
        line_a_color = graphics.Color(27, 93, 198)
        
        count_label_font = graphics.Font()
        count_label_font.LoadFont("./fonts/4x6.bdf")
        count_label_color = graphics.Color(198, 29, 41)
        
        count_wx_font = graphics.Font()
        count_wx_font.LoadFont("./fonts/4x6.bdf")
        count_wx_color = graphics.Color(204, 171, 40)
        
        ticker_font = graphics.Font()
        ticker_font.LoadFont("./fonts/8x13.bdf")
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
        print 'Work Started: PID %d' % os.getpid()
        
        jobs = []
        lock = Lock()
        
        #Process Variables
        time_now = Array('c', b'88/88/88 88:88' ,lock=lock) 
        count_down = Array('c', b'8888Days 88H 88M' ,lock=lock)

        #Start TWITTER WORKER
        rt = Process(target=twitter.tweet_query)
        jobs.append(rt)
        rt.start()

        #Start WEATHER WORKER
        rt = Process(target=weather.get_temp)
        jobs.append(rt)
        rt.start()

        #Start LED_CLOCK LOOP
        rt = Process(target=led_clock)
        jobs.append(rt)
        rt.start()
        
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
    