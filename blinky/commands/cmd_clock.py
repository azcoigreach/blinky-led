from pathlib import Path
import time
import datetime

import click
from PIL import Image, ImageDraw, ImageFont

from blinky.cli import pass_environment


def _get_font_paths():
    fonts_dir = Path(__file__).resolve().parent.parent / "media" / "fonts"
    return (
        fonts_dir / "4x6.pil",
        fonts_dir / "9x15.pil",
    )


def _update_clock_fields(ctx):
    now = datetime.datetime.now()
    ctx.date_now = now.strftime("%m/%d/%y")
    ctx.time_now = now.strftime("%H:%M:%S")

@click.command("clock", short_help="Matrix Clock")
@pass_environment
def cli(ctx):
    """Matrix Clock"""
    ctx.log(click.style("Running Clock.", fg="cyan"))
    ctx.vlog(click.style("Clock Debug", fg="red"))
    fnt_small_path, fnt_med_path = _get_font_paths()
    fnt_small = ImageFont.load(str(fnt_small_path))
    fnt_med = ImageFont.load(str(fnt_med_path))

    while True:
        image = Image.new("RGB", (ctx.matrix.width, ctx.matrix.height), (0, 0, 0))
        color_a = (194, 112, 29) # orange
        color_b = (29, 167, 194) # cyan
        color_c = (194, 29, 29) # red
        color_d = (29, 194, 45) # green
        color_e = (142, 35, 161) # purple

        _update_clock_fields(ctx)
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, ctx.matrix.width - 1, ctx.matrix.height - 1), fill=(0, 0, 0), outline=(0, 0, 128)) # border
        # Date at top (9x15 font = 15px tall, fits at Y=1)
        draw.text((2, 1), str(ctx.date_now), font=fnt_med, fill=color_b)
        # Time in middle, using smaller font to fit (10x20 won't fit, so use 9x15)
        draw.text((2, 16), str(ctx.time_now), font=fnt_med, fill=color_e)
        ctx.vlog(click.style("Matrix Set", fg="red"))  
        ctx.matrix.SetImage(image)
        time.sleep(1)  

