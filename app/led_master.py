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


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('led_master')


class RunText(BlinkyBase):
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        logger.info('Init LED Loop')

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
            self.clock = time_now.value
            self.count_down = count_down.value
            
            #Lines
            graphics.DrawLine(offscreenCanvas, 0, 18, 128, 18, line_a_color)
            graphics.DrawLine(offscreenCanvas, 68, 19, 68, 32, line_a_color)
            
            # Top Twitter Ticker
            if curr_tweet.value != '': 
                ticker = curr_tweet.value
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
            self.temp = str('%sF') % curr_temp.value
            graphics.DrawText(offscreenCanvas, count_wx_font, 104, 25, count_wx_color, self.temp)
            
            # Refresh Rate    
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
            logger.debug('Current Time: %s',time_now.value)
            time.sleep(2)


class countdown_clock():
    def __init__(self, *args, **kwargs):
        while True:
            dt = datetime.datetime
            count = dt(2021,1,21,9) - dt.now()
            count_down.value = '%dDays %dH %dM' % (count.days, count.seconds/3600, count.seconds%3600/60)
            logger.debug('Count Clock: %s', count_down.value)
            time.sleep(2)
    
class weather():
    def __init__(self, *args, **kwargs):
        while True:
            logger.warning('Fetching weather.')
            f = urllib2.urlopen('http://api.wunderground.com/api/38c037db62bd609c/geolookup/conditions/q/AZ/Goodyear.json')
            json_string = f.read()
            parsed_json = json.loads(json_string)
            location = parsed_json['location']['city']
            t = parsed_json['current_observation']['temp_f']
            self.temp = t
            curr_temp.value = self.temp
            logger.info('Temp Update: %s', curr_temp.value)
            time.sleep(900)


class rss_feed():
    def __init__(self, *args, **kwargs):
        self.BITLY_ACCESS_TOKEN = "b6eeb2e971399411b0c5ee15db56b2c353e97e9d"
        self.items=[]
        self.displayItems=[]
        self.feeds=["http://rss.cnn.com/rss/cnn_allpolitics.rss",
                    # "http://hosted2.ap.org/atom/APDEFAULT/89ae8247abe8493fae24405546e9a1aa",
                    # "http://feeds.reuters.com/Reuters/PoliticsNews"
                    ]
        dt = datetime.datetime
        self.font_name = "/usr/share/fonts/truetype/freefont/FreeMono.ttf"
        self.font_size = 17
        
        self.refresh_sec = 1800
        t = dt.now()
        logger.info("News Fetched at %s\n",t.strftime('%m/%d/%y %H:%M:%S'))
              
        threading.Timer(self.refresh_sec, rss_feed).start()
        self.createLinks()
        
        self.fileQueue()
    
    def populateItems(self):
        ticker_ready.value = 0
        del self.items[:]
        del self.displayItems[:]
        os.system("find . -name \*.ppm -delete")
        
        for url in self.feeds:
            self.feed=feedparser.parse(url)
            posts=self.feed["items"]
            for post in posts:
                self.items.append(post)
    
    def getConnection(self):
        try:
            access_token=self.BITLY_ACCESS_TOKEN
            bitly=bitly_api.Connection(access_token=access_token)
            logger.warning('Connected to Bitly')
        except Exception as err:
            logger.error('Bitly error: %s', err)
            time.sleep(30)
            getConnection()
        return bitly    
    
    def createLinks(self):
        try:
            self.populateItems()
            bitlink=self.getConnection()
            for idx, item in enumerate(self.items):
                data=bitlink.shorten(item["link"])
                data=bitlink.shorten(item["link"])
                self.writeImage(unicode(item["title"])+" bit.ly/"+data["hash"], idx)
                logger.info('Bitly: %s',unicode(item["title"]))
                logger.info("bit.ly/%s",data["hash"])
                time.sleep(1)
        except ValueError:
            info.error("Could not create Bitly links")
            ticker_ready.value = 0
        
        finally:
            dt = datetime.datetime
            t = dt.now()+datetime.timedelta(seconds=self.refresh_sec)
            logger.info("Will get more news at %s"), t.strftime('%m/%d/%y %H:%M:%S')
            ticker_ready.value = 1
            
    def writeImage(self, url, count):
        bitIndex=url.find("bit.ly")
        link, headLine=url[bitIndex:], url[:bitIndex]
        def randCol(self):
            return (random.randint(62,255), random.randint(62,255), random.randint(62,255))
        text = ((headLine, randCol(self)), (link, (10, 10, 255)))
        font = ImageFont.truetype(self.font_name, self.font_size)
        all_text = ""
        for text_color_pair in text:
            t = text_color_pair[0]
            all_text = all_text + t
        width, ignore = font.getsize(all_text)
        im = Image.new("RGB", (width + 1, 18), "black")
        draw = ImageDraw.Draw(im)
        x = 0;
        for text_color_pair in text:
            t = text_color_pair[0]
            c = text_color_pair[1]
            draw.text((x, 0), t, c, font=font)
            x = x + font.getsize(t)[0]
        filename=str(count)+".ppm"
        self.displayItems.append(filename)
        im.save(filename)
    
    def fileQueue(self):
        for disp in self.displayItems[:60]:
            news_ticker.value = disp
            logger.info(news_ticker.value)
            time.sleep(30)

class pb_main():
    def __init__(self, *args, **kwargs):
        logger.warning('PB Started...')
        pb_limit = 20
        pb_interval = 20
        pb_auth_token = 'o.1mYHkPzpFzSXHF4M2UcGhit6zyZQ98tM'
        HTTP_PROXY_HOST = None
        HTTP_PROXY_PORT = None
        while True:
            pb = Pushbullet(pb_auth_token)
            pushes = pb.get_pushes(limit=pb_limit)
            output = json.dumps(pushes)
            loop_len = len(pushes)
            count = 0
            for i in pushes:
                if count <= loop_len:
                    try:
                        logger.info(i['title']+' | '+i['url'])
                        time.sleep(pb_interval)
                    except Exception as err:
                        logger.error('PB Error: %s', err)
                        pass
                    count = count + 1
                else:
                    pb_main()
    

class tweet_query():
    def __init__(self, *args, **kwargs):
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
                curr_tweet.value = self.output
            except Exception as err:
                logger.error('Tweet Query Error: %s', err)
                time.sleep(10)
                tweet_query()
            time.sleep(30)


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
        
        apps = ['led_update','tweet_query','led_clock','countdown_clock','weather']
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
                sleep(0.5)
                if p.exitcode is None and not p.is_alive(): # Not finished and not running
                    # Do your error handling and restarting here assigning the new process to processes[n]
                    logger.warning('is gone as if never born!',a)
                elif p.exitcode < 0:
                    logger.warning('Process Ended with an error or a terminate', a)
                    # Handle this either by restarting or delete the entry so it is removed from list as for else
                else:
                    logger.warning('finished',a)
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
    