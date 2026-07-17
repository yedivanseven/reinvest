from collections.abc import Hashable
from pandas import DataFrame
from swak.misc import ArgRepr
from ..config import config

__all__ = [
    'Prepender',
    'prepend'
]


class Prepender(ArgRepr):
    """Prepend an ETF's price history with that of another.

    Parameters
    ----------
    date_col: Hashable
        The name of the data column in both ETFs' dataframes.
    quote_col: Hashable
        The name of the price column in the younger ETF's dataframe.
    prepend_col: Hashable
        The name of the price columns in the older ETF's dataframe.

    """

    def __init__(
            self,
            date_col: Hashable,
            quote_col: Hashable,
            prepend_col: Hashable
    ) -> None:
        super().__init__(date_col, quote_col, prepend_col)
        self.date_col = date_col
        self.quote_col = quote_col
        self.prepend_col = prepend_col

    def __call__(self, older: DataFrame, newer: DataFrame) -> DataFrame:
        """Use and older ETF to prepend the pricing history of a younger ETF.

        Parameters
        ----------
        older: DataFrame
            The older ETF pricing history dataframe. Must contain columns
            `date_col` and `prepend_col`.
        newer
            The newer ETF pricing history dataframe. Must contain columns
            `date_col` and `quote_col`.

        Returns
        -------
        DataFrame
            The newer ETF's pricing history dataframe prepended with data
            from the older ETF's pricing history dataframe.

        Warnings
        --------
        The data of the `older` ETF used to prepend the newer one will be
        changed in place. Pass a copy if you use it elsewhere in your project.

        """
        ratio = newer[self.quote_col] / older[self.prepend_col]
        older[self.prepend_col] *= ratio.dropna().iloc[0].item()
        joined = newer.set_index(self.date_col)[[self.quote_col]].join(
            older.set_index(self.date_col)[[self.prepend_col]],
            how='outer'
        )
        joined[self.quote_col] = joined[self.quote_col].mask(
            joined[self.quote_col].isna(),
            joined[self.prepend_col]
        )
        return joined[[self.quote_col]]


prepend = Prepender(
    date_col=config.cols.date,
    quote_col=config.cols.quote,
    prepend_col=config.cols.reinvested
)
