#!/usr/bin/env python 2.7
from time import strftime

__author__ =        "Stranger Production, LLC"
__created__ =       "23 January 2017"
__modified__ =      "05 December 2017"
__version__ =       "0.1.0"
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

logging.basicConfig(level=logging.DEBUG)

class RunText(BlinkyBase):
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        print('Init LED Loop')

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
            graphics.DrawText(offscreenCanvas, count_font, 1, 31, count_color, self.count_down)
            graphics.DrawLine(offscreenCanvas, 0, 18, 128, 18, line_a_color)
            graphics.DrawLine(offscreenCanvas, 68, 19, 68, 32, line_a_color)
            graphics.DrawText(offscreenCanvas, time_font, 71, 31, time_color, self.clock)
            graphics.DrawText(offscreenCanvas, count_label_font, 1, 25, count_label_color, 'NOT MY PRESIDENT!')
            self.temp = str('%sF') % curr_temp.value
            graphics.DrawText(offscreenCanvas, count_wx_font, 104, 25, count_wx_color, self.temp)
            #print(ticker_ready.value)
#             if ticker_ready.value == 1: 
#                 self.image = Image.open(news_ticker.value)
#                 img_width, img_height = self.image.size
#                 len = img_width + led_width
#                 self.pos -= 1
#                 if (self.pos + len < 0):
#                     self.pos = offscreenCanvas.width
#                 offscreenCanvas.SetImage(self.image, self.pos, 0)
#                 
#             elif ticker_ready.value != 1: 
#                 ticker = "Refreshing Data..."
#                 len = graphics.DrawText(offscreenCanvas, ticker_font, self.pos, 14, ticker_color, ticker)
#                 self.pos -= 1
#                 if (self.pos + len < 0):
#                     self.pos = offscreenCanvas.width
                
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
            time.sleep(0.1)


class countdown_clock():
    def __init__(self, *args, **kwargs):
        while True:
            dt = datetime.datetime
            count = dt(2021,1,21,9) - dt.now()
            count_down.value = '%dDays %dH %dM' % (count.days, count.seconds/3600, count.seconds%3600/60)
            #print(count_down.value)
            time.sleep(0.1)
    
class weather():
    def __init__(self, *args, **kwargs):
        while True:
            f = urllib2.urlopen('http://api.wunderground.com/api/38c037db62bd609c/geolookup/conditions/q/AZ/Goodyear.json')
            json_string = f.read()
            parsed_json = json.loads(json_string)
            location = parsed_json['location']['city']
            t = parsed_json['current_observation']['temp_f']
            self.temp = t
            curr_temp.value = self.temp
            print('Temp Update: %s' % curr_temp.value)
            time.sleep(900)


# class rss_feed():
#     def __init__(self, *args, **kwargs):
#         self.BITLY_ACCESS_TOKEN = "b6eeb2e971399411b0c5ee15db56b2c353e97e9d"
#         self.items=[]
#         self.displayItems=[]
#         self.feeds=["http://rss.cnn.com/rss/cnn_allpolitics.rss",
#                     "http://hosted2.ap.org/atom/APDEFAULT/89ae8247abe8493fae24405546e9a1aa",
#                     "http://feeds.reuters.com/Reuters/PoliticsNews"
#                     ]
#         dt = datetime.datetime
#         self.font_name = "/usr/share/fonts/truetype/freefont/FreeMono.ttf"
#         self.font_size = 17
#         
#         self.refresh_sec = 1800
#         t = dt.now()
#         print("News Fetched at %s\n") % t.strftime('%m/%d/%y %H:%M:%S')
#               
#         threading.Timer(self.refresh_sec, rss_feed).start()
#         self.createLinks()
#         
#         self.fileQueue()
#     def populateItems(self):
#         ticker_ready.value = 0
#         del self.items[:]
#         del self.displayItems[:]
#         os.system("find . -name \*.ppm -delete")
#         
#         for url in self.feeds:
#             self.feed=feedparser.parse(url)
#             posts=self.feed["items"]
#             for post in posts:
#                 self.items.append(post)
#     
#     def getConnection(self):
#         access_token=self.BITLY_ACCESS_TOKEN
#         bitly=bitly_api.Connection(access_token=access_token)
#         return bitly    
#     
#     def createLinks(self):
#         try:
#             self.populateItems()
#             bitlink=self.getConnection()
#             for idx, item in enumerate(self.items):
#                 data=bitlink.shorten(item["link"])
#                 data=bitlink.shorten(item["link"])
#                 self.writeImage(unicode(item["title"])+" bit.ly/"+data["hash"], idx)
#                 print(unicode(item["title"]))
#                 print("bit.ly/"+data["hash"]+"\n")
#                 time.sleep(1)
#         except ValueError:
#             print("Could not create Bitly links")
#             ticker_ready.value = 0
#         
#         finally:
#             dt = datetime.datetime
#             t = dt.now()+datetime.timedelta(seconds=self.refresh_sec)
#             print("\nWill get more news at %s\n\n") % t.strftime('%m/%d/%y %H:%M:%S')
#             ticker_ready.value = 1
#             
#     def writeImage(self, url, count):
#         bitIndex=url.find("bit.ly")
#         link, headLine=url[bitIndex:], url[:bitIndex]
#         def randCol(self):
#             return (random.randint(62,255), random.randint(62,255), random.randint(62,255))
#         text = ((headLine, randCol(self)), (link, (10, 10, 255)))
#         font = ImageFont.truetype(self.font_name, self.font_size)
#         all_text = ""
#         for text_color_pair in text:
#             t = text_color_pair[0]
#             all_text = all_text + t
#         width, ignore = font.getsize(all_text)
#         im = Image.new("RGB", (width + 1, 18), "black")
#         draw = ImageDraw.Draw(im)
#         x = 0;
#         for text_color_pair in text:
#             t = text_color_pair[0]
#             c = text_color_pair[1]
#             draw.text((x, 0), t, c, font=font)
#             x = x + font.getsize(t)[0]
#         filename=str(count)+".ppm"
#         self.displayItems.append(filename)
#         im.save(filename)
#     
#     def fileQueue(self):
#         for disp in self.displayItems[:60]:
#             news_ticker.value = disp
#             print(news_ticker.value)
#             time.sleep(30)

class pb_main():
    def __init__(self, *args, **kwargs):
        print('PB Started...')
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
                        print(i['title']+' | '+i['url'])
                        time.sleep(pb_interval)
                    except:
                        pass
                    count = count + 1
                else:
                    pb_main()
    

class tweet_query():
    def __init__(self, *args, **kwargs):
        client = MongoClient('192.168.1.240', 27017)
        db = client.twitter_stream
        while True:
            query = { '$query' : {}, '$orderby' : { '$natural' : -1 } }
            projection = { '_id' : 0, 'user.screen_name' : 1, 'text' : 1 ,'created_at' : 1}
            result = db.twitter_query.find_one(query, projection)
            output = str(result['user']['screen_name'] + ': ' + result['text'] + ': ' + result['created_at']).encode('ascii','ignore')
            print(output)
            time.sleep(15)


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
        curr_tweet = Array('c', b'username: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', lock=lock) 
        
        #Start TWEET_QUERY LOOP
        rt = Process(target=tweet_query)
        jobs.append(rt)
        rt.start()

        #Start LED_CLOCK LOOP
        # rt = Process(target=led_clock)
        # jobs.append(rt)
        # rt.start()
        
        #Start LED_CLOCK LOOP
        # rt = Process(target=countdown_clock)
        # jobs.append(rt)
        # rt.start()
        
        #Start Weather Updater
        # rt = Process(target=weather)
        # jobs.append(rt)
        # rt.start()
        
        #Start RSS Feed Updater
        # rt = Process(target=rss_feed)
        # jobs.append(rt)
        # rt.start()
        
        #Start Pushbullet Listener
        # rt = Process(target=pb_main)
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
    