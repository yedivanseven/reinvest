import yfinance as yf
from pandas import DataFrame
from swak.misc import ArgRepr

__all__ = [
    'YahooTickerHistoryGetter',
    'get_yahoo_ticker_history',
]


class YahooTickerHistoryGetter(ArgRepr):
    """Partial of yfinance's  ticker history function.

    Creates a ``Ticker` instance with the ticker that callable instances are
    called with and calls its ``history`` method with the (keyword) arguments
    provided at instantiation. See the `yfinance documentation
    <https://ranaroussi.github.io/yfinance/reference/yfinance
    .price_history.html#yfinance.scrapers.history.PriceHistory.history>`_
    for a list and explanation of all (keyword) arguments.

    """
    def __init__(
            self,
            period: str = 'max',
            interval: str = '1d',
            start: str | None = None,
            end: str | None = None,
            prepost: bool = False,
            actions: bool = True,
            auto_adjust: bool = True,
            back_adjust: bool = False,
            repair: bool = True,
            keepna: bool = False,
            rounding: bool = False,
            timeout: float = 10,
            raise_errors: bool = False
    ) -> None:
        super().__init__(
            period,
            interval,
            start,
            end,
            prepost,
            actions,
            auto_adjust,
            back_adjust,
            repair,
            keepna,
            rounding,
            timeout,
            raise_errors
        )
        self.period = period
        self.interval = interval
        self.start = start
        self.end = end
        self.prepost = prepost
        self.actions = actions
        self.auto_adjust = auto_adjust
        self.back_adjust = back_adjust
        self.repair = repair
        self.keepna = keepna
        self.rounding = rounding
        self.timeout = timeout
        self.raise_errors = raise_errors

    def __call__(self, ticker: str) -> DataFrame:
        """Retrieve a Yahoo ticker's pricing history.

        Parameters
        ----------
        ticker: str
            The Yahoo ticker to retrieve the pricing history for.

        Returns
        -------
        DataFrame
            A pandas dataframe with the ticker's pricing history.

        """
        return yf.Ticker(ticker).history(
            period=self.period,
            interval=self.interval,
            start=self.start,
            end=self.end,
            prepost=self.prepost,
            actions=self.actions,
            auto_adjust=self.auto_adjust,
            back_adjust=self.back_adjust,
            repair=self.repair,
            keepna=self.keepna,
            rounding=self.rounding,
            timeout=self.timeout,
            raise_errors=self.raise_errors,
        )


get_yahoo_ticker_history = YahooTickerHistoryGetter()
