from pandas import Series
from swak.io import Parquet2DataFrame, DataFrame2Parquet
from swak.loggers import StdLogger
from swak.funcflow.loggers import PassThroughStdLogger
from swak.pd import Join, ColumnSelector, Assign, Drop, Interpolate
from swak.funcflow import (
    Curry,
    Map,
    Pipe,
    Fork,
    Route,
    identity,
    Safe,
    SafeError,
    Split
)
from ..config import config

__all__ = ['load']

CALLBACK = StdLogger(__name__, level=config.log_level)
LOGGER = PassThroughStdLogger(__name__, level=config.log_level)
TMP_COL = 'tmp'


read_parquet = Parquet2DataFrame(config.paths.ext)
read_overview = Curry(read_parquet, config.files.overview)
write_parquet = DataFrame2Parquet(config.paths.proc, overwrite=True)
write_overview = Curry(write_parquet, config.files.overview)
write_timeseries = Curry(write_parquet, config.files.timeseries)


get_inception_date = Pipe(
    LOGGER.debug(lambda x: f'Extracting inception date for ISIN "{x}"'),
    read_parquet,
    Fork(
        lambda df: df.index[0],
        identity,
    )
)

read_etf = Pipe(
    LOGGER.debug(lambda x: f'Reading timeseries for ISIN "{x}"'),
    Fork(
        identity,
        get_inception_date
    )
)

read_etfs = Pipe(
    LOGGER.info(lambda df: f'Reading {len(df)} ETF timeseries'),
    ColumnSelector(config.cols.isin),
    list,
    Map(Safe(read_etf)),
    Split(lambda obj: isinstance(obj, SafeError)),
    Route(
        [0, 1],
        Map(
            lambda error: CALLBACK.error(error.message),
            wrapper=tuple,
            flat=True
        ),
        identity
    ),
    lambda xs: tuple(zip(*xs)),
    Route(
        [(0, 1), 2],
        lambda index, data: Series(data=data, index=index, name=TMP_COL),
        Pipe(lambda x: x, Join(how='outer')),
    ),
    LOGGER.debug('Done processing ETF timeseries'),
)

save_overview = Pipe(
    LOGGER.info('Adding inception dates to ETF overview'),
    Join(on='isin', how='inner'),
    Assign(**{
        config.cols.inception_date: lambda df: df[TMP_COL]
    }),
    Drop(TMP_COL),
    write_overview,
    LOGGER.debug('Done adding inception dates to ETF overview'),
)

read_tickers = Pipe(
    config.etl.tickers,
    LOGGER.info(lambda xs: f'Reading {len(xs)} Yahoo ticker(s)'),
    Map(read_parquet),
    Split(lambda obj: isinstance(obj, SafeError)),
    Route(
        [0, 1],
        Map(
            lambda error: CALLBACK.error(error.message),
            wrapper=tuple,
            flat=True
        ),
        identity
    ),
    tuple,
    Join(how='outer'),
    LOGGER.debug(lambda df: f'Done processing {df.shape[1]} Yahoo ticker(s)'),
)


load = Pipe(
    LOGGER.info('Starting step "load"'),
    LOGGER.info('Reading ETF overview'),
    read_overview,
    LOGGER.debug('Done reading ETF overview'),
    Fork(
        identity,
        read_etfs
    ),
    Route(
        [(0, 1), 2, ()],
        save_overview,
        identity,
        read_tickers,
    ),
    LOGGER.info('Joining ETF and Yahoo timeseries'),
    Join(how='outer'),
    LOGGER.info('Interpolating missing dates in ETF and Yahoo timeseries'),
    Interpolate('time'),
    write_timeseries,
    LOGGER.info('Done with step "load"')
)
