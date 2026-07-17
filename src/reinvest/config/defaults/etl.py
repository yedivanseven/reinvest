from swak.jsonobject import JsonObject

__all__ = ['ETL']


class ETL(JsonObject):
    """ETL related settings."""
    # Fixed
    usd = 'EUR=X'
    # Configurable
    wait: float= 10
    yahoo: list = []

    def tickers(self) -> list[str]:
        """Combine hard-coded and user-provided tickers into one list."""
        return [self.usd, *self.yahoo]
