import importlib.metadata as meta
from swak.jsonobject import JsonObject
from swak.jsonobject.fields import resolve, Maybe
from .etl import ETL
from .paths import Paths
from .cols import Cols
from .files import Files

PACKAGE = __name__.split('.')[0]
VERSION = meta.version(PACKAGE)

__all__ = ['Main']


class Main(JsonObject):
    """Main project configuration class."""
    # Hard-coded
    package = PACKAGE
    version = VERSION
    file = resolve('config.toml')
    # Nested settings
    log_level: int = 10  # 10=debug, 20=info, 30=warning, 40=error, 50=critical
    toml: Maybe[str](resolve) = None
    paths: Paths = Paths()
    files: Files = Files()
    cols: Cols = Cols()
    etl: ETL = ETL()
    # User provided
    universe: resolve = 'Universe.ods'
