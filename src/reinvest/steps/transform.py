from pandas import DataFrame, to_datetime, Series
from swak.io import Parquet2DataFrame, DataFrame2Parquet, Find, JsonReader
from swak.loggers import StdLogger
from swak.funcflow.loggers import PassThroughStdLogger
from swak.funcflow import (
    Curry,
    Map,
    Pipe,
    Fork,
    Route,
    identity,
    Safe
)
from swak.pd import (
    SetIndex,
    Join,
    Drop,
    RowsSelector,
    ColumnSelector,
    ColumnsSelector,
    Assign,
    ResetIndex,
)
from ..etl import prepend
from ..config import config

__all__ = ['transform']

CALLBACK = StdLogger(__name__, level=config.log_level)
LOGGER = PassThroughStdLogger(__name__, level=config.log_level)


read_json = JsonReader()
read_parquet = Parquet2DataFrame(config.paths.raw_parquet)
read_overview = Curry(read_parquet, config.files.overview)
write_parquet = DataFrame2Parquet(config.paths.ext, overwrite=True)
write_overview = Curry(write_parquet, config.files.overview)


load_universe = Pipe(
    LOGGER.info('Loading Universe'),
    read_overview,
    SetIndex(config.cols.isin),
    Assign(**{
        config.cols.prepends: lambda df: (
            df.get(config.cols.prepends, Series([None] * len(df), dtype=str))
        )
    }),
    LOGGER.debug('Done loading Universe'),
)

load_overviews = Pipe(
    LOGGER.info('Search for ETF Overviews'),
    Find(config.paths.raw, suffix='json'),
    LOGGER.debug(lambda xs: f'Found {len(xs)} ETF Overviews'),
    Map(read_json),
    DataFrame.from_records,
    LOGGER.info(lambda df: f'Loaded {len(df)} ETF Overviews'),
)

load_overview = Pipe(
    LOGGER.info('Enriching Universe with Overviews'),
    Fork(
        load_overviews,
        load_universe
    ),
    Join(on=config.cols.isin, how='right', rsuffix='_user_provided'),
    Drop(config.cols.drop, errors='ignore'),
    Assign(**{
        config.cols.inception_date: lambda df: (
            to_datetime(df[config.cols.inception_date], dayfirst=True)
        ),
        config.cols.holdings_date: lambda df: (
            to_datetime(df[config.cols.holdings_date], dayfirst=True)
        ),
    }),
    ResetIndex(drop=True),
    LOGGER.debug('Done enriching Universe with Overviews')
)

load_ticker = Pipe(
    LOGGER.debug(lambda x: f'Loading ticker "{x}"'),
    read_parquet,
    Assign(**{
        config.cols.date: lambda df: to_datetime(
            df[
                config.cols.DATE
            ].dt.tz_convert(
                'Europe/Berlin'
            ).dt.tz_localize(None).dt.date
        )
    }),
    ColumnsSelector(config.cols.date, config.cols.CLOSE),
    SetIndex(config.cols.date),
)


prepend_etf = Pipe(
    LOGGER.debug(lambda x, y: f'Prepending ISIN "{y}" with ISIN "{x}'),
    Route(
        [0, 1, 1],
        read_parquet,
        read_parquet,
        identity,
    ),
    Route(
        [(0, 1), 2],
        prepend,
        identity,
    ),
    lambda df, isin: (
        df.rename(columns={config.cols.quote: isin}),
        isin
    ),
    LOGGER.debug(lambda _, x: f'Done prepending ISIN "{x}"'),
    write_parquet
)

prepend_etfs = Pipe(
    RowsSelector(
        lambda row: row[config.cols.prepends].notna()
    ),
    LOGGER.info(lambda df: f'Prepending {len(df)} ETFs'),
    ColumnsSelector([config.cols.isin, config.cols.prepends]),
    lambda df: zip(*df.values.tolist()),
    tuple,
    Map(Safe(prepend_etf), wrapper=list, flat=True),
    Map(
        lambda error: CALLBACK.error(error.message),
        wrapper=tuple,
        flat=True
    ),
    LOGGER.debug('Done prepending ETFs'),
)


copy_etf = Pipe(
    LOGGER.debug(lambda x: f'Copying ISIN "{x}"'),
    Fork(
        Pipe(
            read_parquet,
            SetIndex(config.cols.date),
            ColumnsSelector(config.cols.quote)
        ),
        identity
    ),
    lambda df, isin: (
        df.rename(columns={config.cols.quote: isin}),
        isin
    ),
    LOGGER.debug(lambda _, x: f'Done copying ISIN "{x}"'),
    write_parquet
)

copy_etfs = Pipe(
    RowsSelector(
        lambda row: row[config.cols.prepends].isna()
    ),
    LOGGER.info(lambda df: f'Copying {len(df)} ETFs'),
    ColumnSelector('isin'),
    list,
    Map(Safe(copy_etf), flat=True),
    Map(
        lambda error: CALLBACK.error(error.message),
        wrapper=tuple,
        flat=True
    ),
    LOGGER.debug('Done copying ETFs'),
)


clean_etfs = Pipe(
    LOGGER.info('Start cleaning ETFs'),
    load_overview,
    Fork(
        prepend_etfs,
        copy_etfs,
        identity
    ),
    RowsSelector(
        lambda row: row[config.cols.prepends].isna()
    ),
    Drop(config.cols.prepends),
    ResetIndex(drop=True),
    write_overview,
    LOGGER.info('Done cleaning ETFs'),
)


clean_ticker = Pipe(
    LOGGER.debug(lambda x: f'Start cleaning ticker "{x}"'),
    Fork(
        load_ticker,
        identity,
    ),
    lambda df, ticker: (
        df.rename(columns={config.cols.CLOSE: ticker}),
        ticker
    ),
    LOGGER.debug(lambda _, x: f'Saving ticker "{x}"'),
    write_parquet,
)

clean_tickers = Pipe(
    LOGGER.info('Cleaning Yahoo tickers'),
    config.etl.tickers,
    LOGGER.info(lambda xs: f'Processing {len(xs)} ticker(s)'),
    Map(Safe(clean_ticker), flat=True),
    Map(
        lambda error: CALLBACK.error(error.message),
        wrapper=tuple,
        flat=True
    ),
    LOGGER.info('Done cleaning Yahoo tickers'),
)


transform = Pipe(
    LOGGER.info('Starting step "transform"'),
    Fork(
        clean_tickers,
       clean_etfs
    ),
    LOGGER.info('Done with step "transform"')
)
