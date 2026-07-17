from swak.jsonobject import JsonObject
from swak.jsonobject.fields import Strip

__all__ = ['Cols']


class Cols(JsonObject):
    """Hard-coded and user-provided dataframe column names."""
    name = 'name'  # Legacy leftover from original Universe format
    # ETF
    date = 'date'
    quote = 'quote'
    reinvested = 'quote_with_reinvested_dividends'
    inception_date = 'inception_date'
    holdings_date = 'holdings_date'
    drop = [
        'strategy_risk',
        'gettex',
        'prepended_by'  # Legacy leftover from original Universe format
    ]
    # Yahoo
    DATE = 'Date'
    CLOSE = 'Close'
    # Configurable
    isin: Strip() = 'isin'
    prepends: Strip() = 'prepends'
