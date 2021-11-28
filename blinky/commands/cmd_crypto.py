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
        ctx.vlog(click.style(f"Request(sec): {response.elapsed.total_seconds()}", fg='bright_red', reverse=False))
    except Exception as e :
        err_refesh = 15
        ctx.log(click.style(f'Error: {e}', fg='red'))
        ctx.log(click.style(f'Trying again in {err_refesh}s', fg='yellow'))
        time.sleep(err_refesh)

@pass_environment
def markPriceRange(ctx,x,y):
    range = y-x
    pixel_price = ((float(ctx.json_data['highPrice'])-float(ctx.json_data['lowPrice']))/range)
    ctx.curr_pixel = int(round(((float(ctx.json_data['lastPrice'])-float(ctx.json_data['lowPrice'])))/pixel_price))
    if ctx.curr_pixel < x:
        ctx.curr_pixel = x
    elif ctx.curr_pixel > y:
        ctx.curr_pixel = y
    ctx.vlog(click.style(f'ctx.curr_pixel = {ctx.curr_pixel}', fg='yellow'))

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
    "-c",
    "--currency",
    "currency",
    type=str,
    default="$",
    help="Currency symbol ex.'$','B' or 'T'"
    )
@click.option(
    "-d",
    "--decimals",
    "decimals",
    type=int,
    default=2,
    help="Round value for price"
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
def cli(ctx, symbol, refresh, currency, decimals):
    """Retrieve 24hr Crpto Price from Binance API
    Output to Matrix"""
    ctx.log(click.style("Running Crypto.", fg="cyan"))
    ctx.vlog(click.style("Crypto Debug", fg="red"))
    fonts_dir = "/home/pi/BlinkyLED/blinky/media/fonts"
    while True:
        image = Image.new("RGB", (ctx.matrix.width, ctx.matrix.height), (0,0,0))  
        fnt_small = ImageFont.load(f"{fonts_dir}/4x6.pil")
        fnt_med = ImageFont.load(f"{fonts_dir}/7x13.pil")
        fnt_big = ImageFont.load(f"{fonts_dir}/8x13.pil")
        color_a = (194, 112, 29) # orange
        color_b = (29, 167, 194) # cyan
        color_c = (145, 29, 23) # red
        color_d = (25, 145, 23) # green
        color_e = (142, 35, 161) # purple
        color_f = (212, 212, 32) # yellow
        binance(symbol)     
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 127, 31), fill=(0, 0, 0), outline=(0, 0, 128)) # border
        draw.text((1, -1), ctx.json_data['symbol'], font=fnt_med, fill=color_a) # symbol
        # center lastPrice
        lastPrice = str(f"{currency}{round(float(ctx.json_data['lastPrice']),decimals)}")
        lastPrice_w, lastPrice_h = draw.textsize(lastPrice, font=fnt_big)
        draw.text(((ctx.matrix.width-lastPrice_w)/2, 19), lastPrice, font=fnt_big, fill=color_b)
        # priceChange
        draw.text((65, 1), str(f"{currency}{round(float(ctx.json_data['priceChange']),decimals)}"), font=fnt_small, fill=color_e) # priceChange
        draw.text((65, 7), str(f"{round(float(ctx.json_data['priceChangePercent']),decimals)}%"), font=fnt_small, fill=color_e) # priceChangePercent
        # markPriceRange
        markPriceRange(1,126) # pixel value range x,y
        draw.rectangle((1,18,(ctx.curr_pixel),19), fill=color_d) # draw low markPriceRange
        draw.rectangle(((ctx.curr_pixel),18,126,19), fill=color_c) # draw high markPriceRange
        draw.rectangle((ctx.curr_pixel,17,ctx.curr_pixel,20), fill=color_b) # draw current markPriceRange
        # high low values
        draw.text((1, 12), str(f"L:{currency}{round(float(ctx.json_data['lowPrice']),decimals)}"), font=fnt_small, fill=color_f)
        highPrice = str(f"H:{currency}{round(float(ctx.json_data['highPrice']),decimals)}")
        highPrice_w, highPrice_h = draw.textsize(highPrice, font=fnt_small)
        draw.text(((ctx.matrix.width-highPrice_w), 12), highPrice, font=fnt_small, fill=color_f)
        # set image
        ctx.matrix.SetImage(image)
        # log display
        ctx.log(click.style(str(f"{ctx.json_data['symbol']} {currency}{round(float(ctx.json_data['lastPrice']),decimals)}"), fg="yellow"))  
        ctx.log(click.style(str(f"{currency}{round(float(ctx.json_data['priceChange']),decimals)} {round(float(ctx.json_data['priceChangePercent']),decimals)}%"), fg="magenta"))
        ctx.log(click.style(str(f"Low:{currency}{round(float(ctx.json_data['lowPrice']),decimals)} High:{currency}{round(float(ctx.json_data['highPrice']),decimals)}"), fg="cyan"))
        time.sleep(refresh)
        clear = lambda: os.system('clear')
        clear()  

