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