from blinky.cli import pass_environment
import os
import click
from PIL import Image, ImageDraw, ImageFont
import time
import datetime

@pass_environment
def clock(ctx):
    dt = datetime.datetime
    t = dt.now()
    ctx.date_now = t.strftime('%m/%d/%y')
    ctx.time_now = t.strftime('%H:%M:%S')
    ctx.log(ctx.date_now)
    ctx.log(ctx.time_now)

@click.command("clock", short_help="Matrix Clock")
@pass_environment
def cli(ctx):
    """Matrix Clock"""
    ctx.log(click.style("Running Clock.", fg="cyan"))
    ctx.vlog(click.style("Clock Debug", fg="red"))

    while True:
        image = Image.new("RGB", (128, 32), (0,0,0))  
        fnt_small = ImageFont.load(f"/home/pi/BlinkyLED/blinky/media/fonts/4x6.pil")
        fnt_med = ImageFont.load(f"/home/pi/BlinkyLED/blinky/media/fonts/9x15.pil")
        fnt_big = ImageFont.load(f"/home/pi/BlinkyLED/blinky/media/fonts/10x20.pil")
        color_a = (194, 112, 29) # orange
        color_b = (29, 167, 194) # cyan
        color_c = (194, 29, 29) # red
        color_d = (29, 194, 45) # green
        color_e = (142, 35, 161) # purple

        clock()      
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 127, 31), fill=(0, 0, 0), outline=(0, 0, 128)) # border
        draw.text((2, 1), str(ctx.date_now), font=fnt_med, fill=color_b)
        draw.text((45, 13), str(ctx.time_now), font=fnt_big, fill=color_e)
        ctx.vlog(click.style("Matrix Set", fg="red"))  
        ctx.matrix.SetImage(image)
        time.sleep(1)
        clear = lambda: os.system('clear')
        clear()  

