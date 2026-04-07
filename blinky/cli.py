import os
if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.\nPlease try again with 'sudo'. Exiting.")
import sys
import click
from rgbmatrix import RGBMatrix, RGBMatrixOptions


class PiomatterMatrix:
    """Wrapper around Adafruit PioMatter to expose the same interface as hzeller RGBMatrix."""

    _PINOUT_MAP = {
        'adafruit-hat':     'AdafruitMatrixHat',
        'adafruit-hat-pwm': 'AdafruitMatrixHat',
        'adafruit-bonnet':  'AdafruitMatrixBonnet',
    }

    def __init__(self, width, height, n_addr_lines, hardware_mapping):
        import numpy as np
        from adafruit_blinka_raspberry_pi5_piomatter import (
            Colorspace, Geometry, Orientation, Pinout, PioMatter
        )
        self.width = width
        self.height = height
        self._np = np
        pinout_name = self._PINOUT_MAP.get(hardware_mapping, 'AdafruitMatrixHat')
        pinout = getattr(Pinout, pinout_name)
        geometry = Geometry(
            width=width,
            height=height,
            n_addr_lines=n_addr_lines,
            rotation=Orientation.Normal,
        )
        self._framebuffer = np.zeros(shape=(height, width, 3), dtype=np.uint8)
        self._matrix = PioMatter(
            colorspace=Colorspace.RGB888Packed,
            pinout=pinout,
            framebuffer=self._framebuffer,
            geometry=geometry,
        )

    def SetImage(self, image):
        self._framebuffer[:] = self._np.asarray(image)
        self._matrix.show()

    def Clear(self):
        self._framebuffer[:] = 0
        self._matrix.show()

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
    default=32,
    show_default=True,
    help="RGB Matrix rows"
    )
@click.option(
    "--cols",
    "cols",
    type=int,
    default=32,
    show_default=True,
    help="RGB Matrix columns per panel (typically 32 or 64)"
    )
@click.option(
    "-l",
    "--chain_length",
    "chain_length",
    type=int,
    default=4,
    show_default=True,
    help="RGB Matrix chain_length"
    )
@click.option(
    "-p",
    "--parallel",
    "parallel",
    type=int,
    default=1,
    show_default=True,
    help="RGB Matrix parallel"
    )
@click.option(
    "-b",
    "--brightness",
    "brightness",
    type=int,
    default=100,
    show_default=True,
    help="Brightness level. Range: 1..100"
    )

@click.option(
    "--gpio_slowdown",
    "gpio_slowdown",
    type=int,
    default=4,
    show_default=True,
    help="Slow down writing to GPIO. Range: 0..4"
    )
@click.option(
    "--pwm_lsb_nanoseconds",
    "pwm_lsb_nanoseconds",
    type=int,
    default=130,
    show_default=True,
    help="Base time-unit for the on-time in the lowest significant bit in nanoseconds. Range 50..3000"
    )
@click.option(
    "--scan_mode",
    "scan_mode",
    type=int,
    default=0,
    show_default=True,
    help="Progressive or interlaced scan. 0 Progressive, 1 Interlaced"
    )
@click.option(
    "--hardware_mapping",
    "hardware_mapping",
    type=str,
    default='adafruit-hat-pwm',
    show_default=True,
    help="Hardware Mapping - 'regular' , 'adafruit-hat' or 'adafruit-hat-pwm'"
    )
@click.option(
    "--disable_hardware_pulsing",
    "disable_hardware_pulsing",
    is_flag=True,
    default=True,
    show_default=True,
    help="Disable hardware pulse generator; useful on some Pi/kernel combinations"
    )
@click.option(
    "--drop_privileges/--no-drop_privileges",
    "drop_privileges",
    default=False,
    show_default=True,
    help="Drop privileges after startup"
    )
@click.option(
    "--backend",
    "backend",
    type=click.Choice(['rgbmatrix', 'piomatter'], case_sensitive=False),
    default='piomatter',
    show_default=True,
    help="Matrix backend: 'rgbmatrix' (Pi 1-4, patched Pi 5) or 'piomatter' (Pi 5 official)"
    )
@click.option(
    "--n_addr_lines",
    "n_addr_lines",
    type=int,
    default=4,
    show_default=True,
    help="[piomatter] Number of address lines (4 for 32-row panels, 5 for 64-row panels)"
    )
@pass_environment
def cli(ctx, verbose, home, rows, cols, chain_length, parallel, brightness, gpio_slowdown, pwm_lsb_nanoseconds, scan_mode, hardware_mapping, disable_hardware_pulsing, drop_privileges, backend, n_addr_lines):
    """Blinky Matrix Display Driver"""
    ctx.verbose = verbose
    if home is not None:
        ctx.home = home

    # Configuration for the matrix
    options = RGBMatrixOptions()
    options.rows = rows
    ctx.vlog(click.style(f"rows = {options.rows}", fg="yellow"))
    options.cols = cols
    ctx.vlog(click.style(f"cols = {options.cols}", fg="yellow"))
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
    options.disable_hardware_pulsing = disable_hardware_pulsing
    ctx.vlog(click.style(f"disable_hardware_pulsing = {options.disable_hardware_pulsing}", fg="yellow"))
    options.drop_privileges = drop_privileges
    ctx.vlog(click.style(f"drop_privileges = {options.drop_privileges}", fg="yellow"))
    
    if backend == 'piomatter':
        total_width = cols * chain_length
        ctx.vlog(click.style(f"backend = piomatter, total_width = {total_width}, height = {rows}, n_addr_lines = {n_addr_lines}", fg="yellow"))
        ctx.matrix = PiomatterMatrix(
            width=total_width,
            height=rows,
            n_addr_lines=n_addr_lines,
            hardware_mapping=hardware_mapping,
        )
    else:
        ctx.matrix = RGBMatrix(options=options)
    ctx.vlog(click.style(f"home = {ctx.home}", fg="yellow"))
