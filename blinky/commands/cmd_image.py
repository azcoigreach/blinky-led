from blinky.cli import pass_environment
import os
import click
from PIL import Image
import time

@click.command("image", short_help="Display image")
@click.option(
    "-p",
    "--path",
    "path", 
    type=click.Path(resolve_path=True)
    )
@click.argument(
    'filename', 
    required=True,
    type=click.Path(exists=False)
    )
@pass_environment
def cli(ctx, path, filename):
    """Display image"""
    if path is None:
        path = ctx.home
    ctx.log(click.style(f"Displaying: {click.format_filename(path)}/{click.format_filename(filename)}", fg="cyan"))
    ctx.vlog(click.style("Display Debug", fg="red"))
    image_file = f"{click.format_filename(path)}/{click.format_filename(filename)}"
    image = Image.open(image_file)
    image.thumbnail((ctx.matrix.width, ctx.matrix.height), Image.ANTIALIAS)
    while True:
        ctx.matrix.SetImage(image.convert('RGB'))

        try:
            print("Press CTRL-C to stop.")
            while True:
                time.sleep(100)
        except KeyboardInterrupt:
            os.sys.exit(0)
