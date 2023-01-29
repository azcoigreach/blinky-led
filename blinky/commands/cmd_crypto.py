from blinky.cli import pass_environment, make_sync
# import os
import click
from PIL import Image, ImageDraw, ImageFont
import time
import requests
import json
import asyncio
import aiohttp

'''
click.progress bar to count down the rotation timer
'''
@pass_environment
def rotationTimer(ctx, rotate_rate):
    # make progress bar cyan
    with click.progressbar(length=rotate_rate, label='Rotating in:', fill_char=click.style('#', fg='lightcyan')) as bar:
        for i in range(rotate_rate):
            bar.update(1)
            time.sleep(1)

@pass_environment
def updateTimer(ctx, update_rate):
    # make progress bar cyan
    with click.progressbar(length=update_rate, label='Updating in:', fill_char=click.style('#', fg='cyan')) as bar:
        for i in range(update_rate):
            bar.update(1)
            time.sleep(1)

'''
retrieve ticker/24hr from binance api
reference: https://docs.binance.us/#get-24h-price-change-statistics
update binance data using update_rate
'''
@pass_environment
# @make_sync
async def binance(ctx, wrapper):
    try:
        ctx.vlog(click.style(f"Connecting to Binance", fg="bright_red"))
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.binance.us/api/v3/ticker/24hr') as response:
                json_data = await response.json()
                ctx.vlog(click.style(f"Data: {json_data}", fg="bright_red"))
                return json_data
        
    except Exception as e :
        err_refesh = 15
        ctx.log(click.style(f'Error: {e}', fg='red'))
        ctx.log(click.style(f'Trying again in {err_refesh}s', fg='yellow'))
        time.sleep(err_refesh)

'''
determine price range
'''
@pass_environment
def markPriceRange(ctx,x,y):
    range = y-x
    pixel_price = ((float(ctx.symbol['highPrice'])-float(ctx.symbol['lowPrice']))/range)
    ctx.curr_pixel = int(round(((float(ctx.symbol['lastPrice'])-float(ctx.symbol['lowPrice'])))/pixel_price))
    if ctx.curr_pixel < x:
        ctx.curr_pixel = x
    elif ctx.curr_pixel > y:
        ctx.curr_pixel = y
    ctx.vlog(click.style(f'ctx.curr_pixel = {ctx.curr_pixel}', fg='yellow'))


@click.option(
    "-s",
    "--symbols",
    "symbols",
    type=str,
    default='["BTCUSDT"]',
    show_default=True,
    help="Crypto Pair List ex. -s ['BTCUSDT','ETHUSDT']"
    )
@click.option(
    "-f",
    "--filter",
    "filter",
    type=str,
    default="USD",
    show_default=True,
    help="Filter by currency ex. -f USD"
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
    "--rotate_rate",
    "rotate_rate",
    type=int,
    default=10,
    show_default=True,
    help="Default rotation rate"
    )
@click.option(
    "-u",
    "--update_rate",
    "update_rate",
    type=int,
    default=60,
    show_default=True,
    help="Default update rate"
    )
@click.command("crypto", short_help="Crypto Price from Binance")
@pass_environment
@make_sync
async def cli(ctx, rotate_rate, update_rate, currency, decimals, filter):
    """Retrieve 24hr Crpto Price from Binance API
    Output to Matrix"""
    pass
    ctx.log(click.style("Running Crypto.", fg="cyan"))
    ctx.vlog(click.style("Crypto Debug", fg="red"))
    fonts_dir = "/home/pi/BlinkyLED/blinky/media/fonts"

    

    # start a loop to update data from binance based on update_rate and put into ctx.json_data
    while True:
        ctx.json_data = await binance(ctx)
        for symbol in ctx.json_data:
            if symbol['symbol'] == ctx.symbol['symbol']:
                ctx.symbol = symbol
                break
        ctx.vlog(click.style(f"ctx.symbol: {ctx.symbol}", fg="bright_red"))
        updateTimer(ctx, update_rate)
    


    # while True:
    #     image = Image.new("RGB", (ctx.matrix.width, ctx.matrix.height), (0,0,0))  
    #     fnt_small = ImageFont.load(f"{fonts_dir}/4x6.pil")
    #     fnt_med = ImageFont.load(f"{fonts_dir}/7x13.pil")
    #     fnt_big = ImageFont.load(f"{fonts_dir}/8x13.pil")
    #     color_a = (194, 112, 29) # orange
    #     color_b = (29, 167, 194) # cyan
    #     color_c = (145, 29, 23) # red
    #     color_d = (25, 145, 23) # green
    #     color_e = (142, 35, 161) # purple
    #     color_f = (212, 212, 32) # yellow

    #     binance_json_data = await binance(ctx)     
        
    #     for ctx.symbol in binance_json_data:
    #         # filter by currency USD, USDT, BTC, ETH
    #         if ctx.symbol['symbol'].endswith(ctx.filter):
    #             draw = ImageDraw.Draw(image)
    #             draw.rectangle((0, 0, 127, 31), fill=(0, 0, 0), outline=(0, 0, 128)) # border
    #             draw.text((1, -1), ctx.symbol['symbol'], font=fnt_med, fill=color_a) # symbol
    #             # center lastPrice
    #             lastPrice = str(f"{currency}{round(float(ctx.symbol['lastPrice']),decimals)}")
    #             lastPrice_w, lastPrice_h = draw.textsize(lastPrice, font=fnt_big)
    #             draw.text(((ctx.matrix.width-lastPrice_w)/2, 19), lastPrice, font=fnt_big, fill=color_b)
    #             # priceChange
    #             draw.text((65, 1), str(f"{currency}{round(float(ctx.symbol['priceChange']),decimals)}"), font=fnt_small, fill=color_e) # priceChange
    #             draw.text((65, 7), str(f"{round(float(ctx.symbol['priceChangePercent']),decimals)}%"), font=fnt_small, fill=color_e) # priceChangePercent
    #             # markPriceRange
    #             markPriceRange(1,126) # pixel value range x,y
    #             draw.rectangle((1,18,(ctx.curr_pixel),19), fill=color_d) # draw low markPriceRange
    #             draw.rectangle(((ctx.curr_pixel),18,126,19), fill=color_c) # draw high markPriceRange
    #             draw.rectangle((ctx.curr_pixel,17,ctx.curr_pixel,20), fill=color_b) # draw current markPriceRange
    #             # high low values
    #             draw.text((1, 12), str(f"L:{currency}{round(float(ctx.symbol['lowPrice']),decimals)}"), font=fnt_small, fill=color_f)
    #             highPrice = str(f"H:{currency}{round(float(ctx.symbol['highPrice']),decimals)}")
    #             highPrice_w, highPrice_h = draw.textsize(highPrice, font=fnt_small)
    #             draw.text(((ctx.matrix.width-highPrice_w), 12), highPrice, font=fnt_small, fill=color_f)
    #             # set image
    #             ctx.matrix.SetImage(image)
    #             # log display
    #             ctx.log(click.style(str(f"{ctx.symbol['symbol']} {currency}{round(float(ctx.symbol['lastPrice']),decimals)}"), fg="yellow"))  
    #             ctx.log(click.style(str(f"{currency}{round(float(ctx.symbol['priceChange']),decimals)} {round(float(ctx.symbol['priceChangePercent']),decimals)}%"), fg="magenta"))
    #             ctx.log(click.style(str(f"Low:{currency}{round(float(ctx.symbol['lowPrice']),decimals)} High:{currency}{round(float(ctx.symbol['highPrice']),decimals)}"), fg="cyan"))
    #             # rotate_rate timer
    #             rotationTimer(rotate_rate)
    #             # clear = lambda: os.system('clear')
    #             click.clear()
    #         # update

