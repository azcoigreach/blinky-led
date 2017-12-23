#!/usr/bin/env python 2.7
import time
from time import strftime
import os
from multiprocessing import Process, Manager
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

def led_clock(d):
    logger.warning('Init Clock')
    while True:
        dt = datetime.datetime
        dt_now = dt.now().strftime('%m/%d/%y %H:%M')
        d['time_now'] = str(dt_now)
        logger.debug('Current Time: %s',d['time_now'])
        
        time.sleep(10)

def led_update(d):
    logger.debug('led_update function')
    
    global d_time_now, d_count_down, d_curr_tweet, d_curr_temp

    d_time_now = d['time_now']
    d_count_down = d['count_down']
    d_curr_tweet = d['curr_tweet']
    d_curr_temp = d['curr_temp']

    parser = RunText()
    if (not parser.process()):
        parser.print_help()





if __name__ == "__main__":
    try:
        logger.warning('Work Started: PID %d', os.getpid())
        manager = Manager()
        d = manager.dict()
        d['time_now'] = ''
        d['count_down'] = ''
        d['curr_tweet'] = ''
        d['curr_temp'] = ''
        logger.debug(d)
        apps = [led_clock, led_update]# weather.weather, .led_clock, countdown_clock.countdown_clock, tweet_query.tweet_query, led_update.led_update] 
        processes = {}
        n=0
        for app in apps:
            instance = app(d)
            p = Process(target=instance, args=(d,), name=app)
            p.start()
            # processes[n] = (p, app)
            logger.warning(p) 
            n += 1
            time.sleep(0.25)

        # while len(processes) > 0:
        #     for n in processes.keys():
        #         (p, a) = processes[n]
                
        #         time.sleep(0.5)
        #         if p.exitcode is None and not p.is_alive(): # Not finished and not running
        #             # Do your error handling and restarting here assigning the new process to processes[n]
        #             # logger.warning('is gone as if never born!',p)
        #         elif p.exitcode < 0:
        #             # logger.warning('Process Ended with an error or a terminate', p)
        #             # Handle this either by restarting or delete the entry so it is removed from list as for else
        #         else:
        #             # logger.warning('finished', p)
        #             p.join() # Allow tidyup
        #             del processes[n] # Removed finished items from the dictionary 
        #             # When none are left then loop will end
        
            
    except KeyboardInterrupt:
        for n in processes.keys():
            (p, a) = processes[n]
            logger.warning('Shutting Down: %s %s', p, p.is_alive())
            p.terminate()
            time.sleep(2)
            
    