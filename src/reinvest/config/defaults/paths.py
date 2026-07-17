from pathlib import Path
from swak.jsonobject import JsonObject
from swak.jsonobject.fields import resolve

__all__ = ['Paths']


class Paths(JsonObject):
    """Working directory and path settings"""
    workdir: resolve = Path.cwd()

    @property
    def data(self) -> Path:
        """Data directory."""
        return Path(self.workdir) / 'data'

    @property
    def raw(self) -> str:
        """Raw data sub-folder."""
        return str(self.data / 'raw')

    @property
    def raw_json(self) -> str:
        """JSON suffix template for the raw data sub-folder."""
        return self.raw + '/{}.json'

    @property
    def raw_parquet(self) -> str:
        """Parquet suffix template for the raw data sub-folder."""
        return self.raw + '/{}.parquet'

    @property
    def ext(self) -> str:
        """Parquet suffix template for the extended data sub-folder."""
        return str(self.data / 'ext' / '{}.parquet')

    @property
    def proc(self) -> str:
        """Parquet suffix template for the processed data sub-folder."""
        return str(self.data / 'proc' / '{}.parquet')
