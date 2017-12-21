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