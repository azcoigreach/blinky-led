#!/usr/bin/env python 2.7
import time
from time import strftime
import os
from multiprocessing import Process, Manager, Lock, Array, Value
import pprint
from blinkybase import BlinkyBase
from rgbmatrix import graphics
import datetime

from workers import *
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class RunText(BlinkyBase):
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        logger.warning('Init LED Loop')

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
        
        while True:
            offscreenCanvas.Clear()
            logger.debug(d_time_now)
            self.clock = d_time_now
            self.count_down = d_count_down
            
            #Lines
            graphics.DrawLine(offscreenCanvas, 0, 18, 128, 18, line_a_color)
            graphics.DrawLine(offscreenCanvas, 68, 19, 68, 32, line_a_color)
            
            # Top Twitter Ticker
            if d_curr_tweet != '': 
                logger.debug(d_curr_tweet)
                ticker = d_curr_tweet
                len = graphics.DrawText(offscreenCanvas, ticker_font, self.pos, 14, ticker_color, ticker)
                self.pos -= 1
                if (self.pos + len < 0):
                    self.pos = offscreenCanvas.width
            
            #Bottom Right Clock
            graphics.DrawText(offscreenCanvas, time_font, 71, 31, time_color, self.clock)
            
            #Bottom Left Countdown Clock
            graphics.DrawText(offscreenCanvas, count_font, 1, 31, count_color, self.count_down)
            graphics.DrawText(offscreenCanvas, count_label_font, 1, 25, count_label_color, 'NOT MY PRESIDENT!')
            
            # Bottom Right Weather Bug
            self.temp = str('%sF') % d_curr_temp
            graphics.DrawText(offscreenCanvas, count_wx_font, 104, 25, count_wx_color, self.temp)
            
            # Refresh Rate    
            time.sleep(0.025)
            offscreenCanvas = self.matrix.SwapOnVSync(offscreenCanvas)

def led_clock():
    logger.warning('Init Clock')
    while True:
        dt = datetime.datetime
        dt_now = dt.now().strftime('%m/%d/%y %H:%M')
        d['time_now'] = str(dt_now)
        logger.debug('Current Time: %s',d['time_now'])
        
        time.sleep(10)

def led_update():
    logger.debug('led_update function')
    
    global d_time_now, d_count_down, d_curr_tweet, d_curr_temp

    d_time_now = d['time_now']
    d_count_down = d['count_down']
    d_curr_tweet = d['curr_tweet']
    d_curr_temp = d['curr_temp']

    parser = RunText()
    if (not parser.process()):
        parser.print_help()



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
        curr_temp = Value('d', 888.8)
        news_ticker = Array('c', b'9999.ppm' ,lock=lock)
        news_ticker.value = str('0.ppm')
        ticker_ready = Value('i', 0)
        
        
        #Start LED_CLOCK LOOP
        rt = Process(target=led_clock)
        jobs.append(rt)
        rt.start()
        
        #Start LED_CLOCK LOOP
        rt = Process(target=countdown_clock)
        jobs.append(rt)
        rt.start()
        
        #Start Weather Updater
        rt = Process(target=weather)
        jobs.append(rt)
        rt.start()
        
        #Start RSS Feed Updater
        # rt = Process(target=rss_feed)
        # jobs.append(rt)
        # rt.start()
        
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
    