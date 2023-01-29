import os
if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.\nPlease try again with 'sudo'. Exiting.")

from .config import matrix

import sys
import click
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import functools
import asyncio

CONTEXT_SETTINGS = dict(auto_envvar_prefix="BLINKY")

class Environment:
    def __init__(self):
        self.verbose = False
        self.home = os.getcwd()

    def log(self, msg, *args):
        """Logs a message to stderr."""
        if args:
            msg %= args
        click.echo(msg, file=sys.stderr)

    def vlog(self, msg, *args):
        """Logs a message to stderr only if verbose is enabled."""
        if self.verbose:
            self.log(msg, *args)
    
    def matrix(self):
        pass

    

pass_environment = click.make_pass_decorator(Environment, ensure=True)
cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "commands"))

def make_sync(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(func(*args, **kwargs))
        return wrapper


class BlinkyCLI(click.MultiCommand):
    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith(".py") and filename.startswith("cmd_"):
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            mod = __import__(f"blinky.commands.cmd_{name}", None, None, ["cli"])
        except ImportError:
            return
        return mod.cli


@click.command(cls=BlinkyCLI, context_settings=CONTEXT_SETTINGS)
@click.option(
    "--home",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    help="Changes the folder to operate on.",
    )
@click.option("-v", "--verbose", 
    is_flag=True, 
    help="Enables verbose mode."
    )
@click.option(
    "-r",
    "--rows",
    "rows",
    type=int,
    default=matrix.rows,
    show_default=True,
    help="RGB Matrix rows"
    )
@click.option(
    "-c",
    "--cols",
    "cols",
    type=int,
    default=matrix.cols,
    show_default=True,
    help="RGB Matrix cols"
    )   
@click.option(
    "-l",
    "--chain_length",
    "chain_length",
    type=int,
    default=matrix.chain_length,
    show_default=True,
    help="RGB Matrix chain_length"
    )
@click.option(
    "-p",
    "--parallel",
    "parallel",
    type=int,
    default=matrix.parallel,
    show_default=True,
    help="RGB Matrix parallel"
    )
@click.option(
    "-b",
    "--brightness",
    "brightness",
    type=int,
    default=matrix.brightness,
    show_default=True,
    help="Brightness level. Range: 1..100"
    )

@click.option(
    "--gpio_slowdown",
    "gpio_slowdown",
    type=int,
    default=matrix.gpio_slowdown,
    show_default=True,
    help="Slow down writing to GPIO. Range: 0..4"
    )
@click.option(
    "--pwm_lsb_nanoseconds",
    "pwm_lsb_nanoseconds",
    type=int,
    default=matrix.pwm_lsb_nanoseconds,
    show_default=True,
    help="Base time-unit for the on-time in the lowest significant bit in nanoseconds. Range 50..3000"
    )
@click.option(
    "--scan_mode",
    "scan_mode",
    type=int,
    default=matrix.scan_mode,
    show_default=True,
    help="Progressive or interlaced scan. 0 Progressive, 1 Interlaced"
    )
@click.option(
    "--hardware_mapping",
    "hardware_mapping",
    type=str,
    default=matrix.hardware_mapping,
    show_default=True,
    help="Hardware Mapping - 'regular' , 'adafruit-hat' or 'adafruit-hat-pwm'"
    )
@click.option(
    "--show_refresh_rate",
    "show_refresh_rate",
    type=int,
    default=matrix.show_refresh_rate,
    show_default=True,
    help="If set, show the current refresh rate on stdout"
    )
@click.option(
    "--inverse_colors",
    "inverse_colors",
    default=matrix.inverse_colors,
    show_default=True,
    help="Switch if your matrix has inverse colors on. 1=Inverse colors, 0=Normal colors"
    )
@click.option(
    "--multiplexing",
    "multiplexing",
    type=int,
    default=matrix.multiplexing,
    show_default=True,
    help="Multiplexing type: 0=direct; 1=Stripe; 2=Checkered; 3=Spiral; 4=ZStripe; 5=ZnMirrorZStripe; 6=coreman; 7=Kaler2Scan; 8=ZStripeUneven"
    )
@click.option(
    "--row_address_type",
    "row_address_type",
    type=int,
    default=matrix.row_address_type,
    show_default=True,
    help="0 = default; 1=AB-addressed panels; 2=row direct; 3=ABC-addressed panels; 4=ABC Shift + DE direct"
    )
@click.option(
    "--disable_hardware_pulsing",
    "disable_hardware_pulsing",
    default=matrix.disable_hardware_pulsing,
    show_default=True,
    help="Don't use hardware pin-pulse generation."
    )
@click.option(
    "--led_rgb_sequence",
    "led_rgb_sequence",
    type=str,
    default=matrix.led_rgb_sequence,
    show_default=True,
    help="Switch if your matrix has led colors swapped. Default: 'RGB'"
    )
@click.option(
    "--pixel_mapper_config",
    "pixel_mapper_config",
    type=str,
    default=matrix.pixel_mapper_config,
    show_default=True,
    help="Comma-separated list of pixel-mapper parameters. Can be given multiple times."
    )
@click.option(
    "--panel_type",
    "panel_type",
    type=str,
    default=matrix.panel_type,
    show_default=True,
    help="Needed to initialize special panels."
    )
@click.option(
    "--limit_refresh_rate_hz",
    "limit_refresh_rate_hz",
    type=int,
    default=matrix.limit_refresh_rate_hz,
    show_default=True,
    help="Limit refresh rate to this frequency in Hz. Useful if you only refresh the display periodically and want to save some power. 0=no limit."
    )
@click.option(
    "--daemon",
    "daemon",
    type=int,
    default=matrix.daemon,
    show_default=True,
    help="Run as daemon. 1=daemon, 0=foreground"
    )
@click.option(
    "--drop_privileges",
    "drop_privileges",
    type=int,
    default=matrix.drop_privileges,
    show_default=True,
    help="Drop privileges from 'root' after initializing the hardware. 1=drop, 0=don't drop"
    )
@pass_environment
@make_sync
async def cli(ctx,
        verbose, 
        home, 
        rows, 
        cols,
        chain_length, 
        parallel, 
        brightness, 
        gpio_slowdown, 
        pwm_lsb_nanoseconds, 
        scan_mode, 
        hardware_mapping, 
        show_refresh_rate, 
        inverse_colors, 
        multiplexing, 
        row_address_type, 
        disable_hardware_pulsing, 
        led_rgb_sequence, 
        pixel_mapper_config, 
        panel_type, 
        limit_refresh_rate_hz, 
        daemon, 
        drop_privileges
        ):
    """Blinky Matrix Display Driver"""
    ctx.verbose = verbose
    if home is not None:
        ctx.home = home

    # Configuration for the matrix
    options = RGBMatrixOptions()
    options.rows = rows
    ctx.vlog(click.style(f"rows = {options.rows}", fg="yellow"))
    options.chain_length = chain_length
    ctx.vlog(click.style(f"chain_length = {options.chain_length}", fg="yellow"))
    options.parallel = parallel
    ctx.vlog(click.style(f"parallel = {options.parallel}", fg="yellow"))
    options.brightness = brightness
    ctx.vlog(click.style(f"brightness = {options.brightness}", fg="yellow"))
    options.gpio_slowdown = gpio_slowdown
    ctx.vlog(click.style(f"gpio_slowdown = {options.gpio_slowdown}", fg="yellow"))
    options.pwm_lsb_nanoseconds = pwm_lsb_nanoseconds
    ctx.vlog(click.style(f"pwm_lsb_nanoseconds = {options.pwm_lsb_nanoseconds}", fg="yellow"))
    options.scan_mode = scan_mode
    ctx.vlog(click.style(f"scan_mode = {options.scan_mode}", fg="yellow"))
    options.hardware_mapping = hardware_mapping
    ctx.vlog(click.style(f"hardware_mapping = {options.hardware_mapping}", fg="yellow"))
    options.show_refresh_rate = show_refresh_rate
    ctx.vlog(click.style(f"show_refresh_rate = {options.show_refresh_rate}", fg="yellow"))
    options.inverse_colors = inverse_colors
    ctx.vlog(click.style(f"inverse_colors = {options.inverse_colors}", fg="yellow"))
    options.multiplexing = multiplexing
    ctx.vlog(click.style(f"multiplexing = {options.multiplexing}", fg="yellow"))
    options.row_address_type = row_address_type
    ctx.vlog(click.style(f"row_address_type = {options.row_address_type}", fg="yellow"))
    options.disable_hardware_pulsing = disable_hardware_pulsing
    ctx.vlog(click.style(f"disable_hardware_pulsing = {options.disable_hardware_pulsing}", fg="yellow"))
    options.led_rgb_sequence = led_rgb_sequence
    ctx.vlog(click.style(f"led_rgb_sequence = {options.led_rgb_sequence}", fg="yellow"))
    options.pixel_mapper_config = pixel_mapper_config
    ctx.vlog(click.style(f"pixel_mapper_config = {options.pixel_mapper_config}", fg="yellow"))
    options.panel_type = panel_type
    ctx.vlog(click.style(f"panel_type = {options.panel_type}", fg="yellow"))
    options.limit_refresh_rate_hz = limit_refresh_rate_hz
    ctx.vlog(click.style(f"limit_refresh_rate_hz = {options.limit_refresh_rate_hz}", fg="yellow"))
    options.daemon = daemon
    ctx.vlog(click.style(f"daemon = {options.daemon}", fg="yellow"))
    options.drop_privileges = drop_privileges
    ctx.vlog(click.style(f"drop_privileges = {options.drop_privileges}", fg="yellow"))
    ctx.vlog(click.style(f"home = {ctx.home}", fg="yellow"))
    ctx.matrix = RGBMatrix(options = options)