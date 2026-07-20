from pandas import DataFrame
import pandas_market_calendars as pdmc
from pandas_market_calendars.market_calendar import MarketCalendar
from swak.misc import ArgRepr

__all__ = [
    'TradingDayFilter',
    'filter_trading_days',
]


class TradingDayFilter(ArgRepr):
    """Filter out non-trading days from a date-index pandas dataframe.

    Parameters
    ----------
    exchange: str, optional
        The name of the exchange to use the trading days of. Use the class
        method :meth:`list_exchanges` to see a list of possible choices.
        Defaults to "XETR", the short name of the electronic Deutsche Börse
        in Frankfurt.

    """

    def __init__(self, exchange: str = 'XETR') -> None:
        super().__init__(exchange)
        self.exchange = exchange

    @classmethod
    def list_exchanges(cls) -> list[str]:
        """Get a list of exchanges that can be used."""
        return pdmc.get_calendar_names()

    @property
    def calendar(self) -> MarketCalendar:
        """The calendar for the chosen exchange"""
        return pdmc.get_calendar(self.exchange)

    def __call__(self, df: DataFrame) -> DataFrame:
        """Filter out non-trading days from a date-index pandas dataframe.

        Parameters
        ----------
        df: DataFrame
            The pandas dataframe to filter. Must have a daily DatetimeIndex.

        Returns
        -------
        DataFrame
            The input dataframe with only non-trading days dropped..

        """
        days = self.calendar.valid_days(
            start_date=df.index.min(),
            end_date=df.index.max()
        ).tz_localize(None)
        return df.loc[days]


filter_trading_days = TradingDayFilter()
