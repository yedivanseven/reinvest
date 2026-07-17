import justetf_scraping as je
from justetf_scraping.etf_profile import EtfOverview
from pandas import DataFrame
from swak.misc import ArgRepr

__all__ = [
    'EtfOverviewGetter',
    'get_etf_overview',
    'get_etf_chart',
]


class EtfOverviewGetter(ArgRepr):
    """Scrape ETF overview data from JustETF.

    Parameters
    ----------
    include_gettex: bool, optional
        Whether to include tan up-to-date quote from gettex.
        Defaults to ``False``.
    expand_allocations: bool, optional
        Whether to expand the individual allocations of the ETF.
        Defaults to ``True``.

    """

    def __init__(
            self,
            include_gettex: bool = False,
            expand_allocations: bool = True,
    ) -> None:
        super().__init__(include_gettex, expand_allocations)
        self.include_gettex = include_gettex
        self.expand_allocations = expand_allocations

    def __call__(self, isin: str) -> EtfOverview:
        """Scrape ETF overview data from JustETF.

        Parameters
        ----------
        isin: str
            The ISIN of the ETF to scrape overview data for.

        Returns
        -------
        dict
            Dictionary with the ETF overview data.

        """
        return je.get_etf_overview(
            isin,
            include_gettex=self.include_gettex,
            expand_allocations=self.expand_allocations
        )


def get_etf_chart(isin: str) -> DataFrame:
    """Scrape ETF pricing history from JustETF.

    Parameters
    ----------
    isin: str
        The ISIN of the ETF to scrape historical price data for.

    Returns
    -------
    DataFrame
        DataFrame with the ETF pricing history data.

    """
    return je.load_chart(isin, currency='EUR', unclosed=False)


get_etf_overview = EtfOverviewGetter()
