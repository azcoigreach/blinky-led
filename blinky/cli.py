import os
if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.\nPlease try again with 'sudo'. Exiting.")

from .config import matrix

import sys
import click
from rgbmatrix import RGBMatrix, RGBMatrixOptions


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
    default=matrix.led_pwm_lsb_nanoseconds,
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
@pass_environment
def cli(ctx, verbose, home, rows, chain_length, parallel, brightness, gpio_slowdown, pwm_lsb_nanoseconds, scan_mode, hardware_mapping):
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
    
    ctx.matrix = RGBMatrix(options = options)
    ctx.vlog(click.style(f"home = {ctx.home}", fg="yellow"))
