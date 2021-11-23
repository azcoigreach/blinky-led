from blinky.cli import pass_environment
import os
import click
from PIL import Image, ImageDraw, ImageFont
import time
import requests

@pass_environment
def binance(ctx, symbol):
    try:
        response = requests.get(f'https://api.binance.us/api/v3/ticker/24hr?symbol={symbol}')
        ctx.json_data = response.json()
        ctx.vlog(click.style(ctx.json_data, fg="red"))
    except Exception as e :
        err_refesh = 15
        ctx.log(click.style(f'Error: {e}', fg='red'))
        ctx.log(click.style(f'Trying again in {err_refesh}s', fg='yellow'))
        time.sleep(err_refesh)

@pass_environment
def markPriceRange(ctx):
    matrix_width = 126
    pixel_price = ((float(ctx.json_data['highPrice'])-float(ctx.json_data['lowPrice']))/matrix_width)
    # ctx.vlog(click.style(f'pixel_price = {pixel_price}', fg='yellow'))
    ctx.curr_pixel = int(round(((float(ctx.json_data['lastPrice'])-float(ctx.json_data['lowPrice'])))/pixel_price))
    ctx.vlog(click.style(f'curr_pixel = {ctx.curr_pixel}', fg='yellow'))

@click.option(
    "-s",
    "--symbol",
    "symbol",
    type=str,
    default="BTCUSDT",
    show_default=True,
    help="Crypto Pair ex.'BTCUSDT'"
)
@click.option(
    "-r",
    "--refresh",
    "refresh",
    type=int,
    default=60,
    show_default=True,
    help="Default refresh rate"
)
@click.command("crypto", short_help="Crypto Price from Binance")
@pass_environment
def cli(ctx, symbol, refresh):
    """Retrieve 24hr Crpto Price from Binance API
    Output to Matrix"""
    ctx.log(click.style("Running Crypto.", fg="cyan"))
    ctx.vlog(click.style("Crypto Debug", fg="red"))

    while True:
        image = Image.new("RGB", (128, 32), (0,0,0))  
        fnt_small = ImageFont.load(f"/home/pi/BlinkyLED/blinky/fonts/4x6.pil")
        fnt_med = ImageFont.load(f"/home/pi/BlinkyLED/blinky/fonts/7x13.pil")
        fnt_big = ImageFont.load(f"/home/pi/BlinkyLED/blinky/fonts/10x20.pil")
        color_a = (194, 112, 29) # orange
        color_b = (29, 167, 194) # cyan
        color_c = (145, 29, 23) # red
        color_d = (25, 145, 23) # green
        color_e = (142, 35, 161) # purple
        binance(symbol)     
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 127, 31), fill=(0, 0, 0), outline=(0, 0, 128)) # border
        draw.text((1, -1), ctx.json_data['symbol'], font=fnt_med, fill=color_a)
        draw.text((1, 15), str(f"${float(ctx.json_data['lastPrice'])}"), font=fnt_big, fill=color_b)
        draw.text((65, 1), str(f"${float(ctx.json_data['priceChange'])}"), font=fnt_small, fill=color_e)
        draw.text((65, 7), str(f"{float(ctx.json_data['priceChangePercent'])}%"), font=fnt_small, fill=color_e)
        markPriceRange()
        draw.rectangle((1,14,(ctx.curr_pixel-1),15), fill=color_d) # Low Range
        draw.rectangle(((ctx.curr_pixel+1),14,126,15), fill=color_c) # High range
        draw.rectangle((ctx.curr_pixel,13,ctx.curr_pixel,16), fill=color_b) # Current value
        # draw.text((1,22), ctx.json_data['highPrice'], font=fnt_small, fill=color_a)
        # draw.text((20,22), ctx.json_data['lowPrice'], font=fnt_small, fill=color_a)
        ctx.vlog(click.style("Matrix Set", fg="red"))  
        ctx.matrix.SetImage(image)
        ctx.log(click.style(str(f"{ctx.json_data['symbol']} ${float(ctx.json_data['lastPrice'])}"), fg="yellow"))  
        ctx.log(click.style(str(f"${float(ctx.json_data['priceChange'])} {float(ctx.json_data['priceChangePercent'])}%"), fg="magenta"))
        ctx.log(click.style(str(f"High:${float(ctx.json_data['highPrice'])} Low:${float(ctx.json_data['lowPrice'])}%"), fg="cyan"))
        time.sleep(refresh)
        clear = lambda: os.system('clear')
        clear()  

