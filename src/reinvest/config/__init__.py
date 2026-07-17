import warnings
from dotenv import load_dotenv
from swak.cli import EnvParser, ArgParser, EPILOG
from swak.io import TomlReader

from .defaults import main, Main

__all__ = [
    'Main',
    'config',
    'actions',
]

# Parse the environment for config options
load_dotenv()
parse_env = EnvParser('RI_')
env_vars = parse_env()
temporary = main(env_vars)

# Parse the command line for config options
ACTIONS = """actions:
dry-run     Print the configuration reinvest would run with.
"""
parse_args = ArgParser(description=ACTIONS, epilog=EPILOG.format(temporary))
actions, args = parse_args()
temporary = temporary(args)

# If a config file is given, ...
if temporary.toml:
    # ... load it and error out if it is not found.
    toml = TomlReader(temporary.toml)()
# If no config file is given, ...
else:
    # ... try to read the default config file ...
    try:
        toml = TomlReader(temporary.file)()
    # ... and warn if it's not found.
    except FileNotFoundError:
        msg = 'No config file "{}" found! Proceeding with defaults.'
        warnings.warn(msg.format(temporary.file))
        toml = {}

config = main(toml)(env_vars)(args)
