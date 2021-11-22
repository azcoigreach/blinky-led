import os
if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.\nPlease try again with 'sudo'. Exiting.")
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
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode.")
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
    "-h",
    "--hardware_mapping",
    "hardware_mapping",
    type=str,
    default='adafruit-hat',
    show_default=True,
    help="Hardware Mapping - 'regular' or 'adafruit-hat'"
)
@pass_environment
def cli(ctx, verbose, home, rows, chain_length, parallel, hardware_mapping):
    """Blinky Matrix Display Driver"""
    ctx.verbose = verbose
    if home is not None:
        ctx.home = home

    # Configuration for the matrix
    options = RGBMatrixOptions()
    options.rows = rows
    options.chain_length = chain_length
    options.parallel = parallel
    options.hardware_mapping = hardware_mapping

    ctx.matrix = RGBMatrix(options = options)
    ctx.vlog(click.style("Matrix cli executed", fg="red"))
    ctx.vlog(click.style(f"home = {ctx.home}", fg="yellow"))
