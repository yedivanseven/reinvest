from swak.pd import ColumnSelector, ResetIndex, Drop, AsType
from swak.loggers import StdLogger
from swak.funcflow.loggers import PassThroughStdLogger
from swak.funcflow import Pipe, Map, Safe, Fork, SideEffect, Curry, Fallback
from swak.io import (
    DataFrame2Parquet,
    JsonWriter,
    Excel2DataFrame,
    Csv2DataFrame
)
from ..config import config
from ..io import (
    wait,
    get_etf_overview,
    get_etf_chart,
    get_yahoo_ticker_history
)
from .logs import universe_cb

__all__ = ['extract']

CALLBACK = StdLogger(__name__, level=config.log_level)
LOGGER = PassThroughStdLogger(__name__, level=config.log_level)


write_parquet = DataFrame2Parquet(config.paths.raw_parquet, overwrite=True)
write_overview = Curry(write_parquet, config.files.overview)
write_json = JsonWriter(config.paths.raw_json, overwrite=True)
read_universe = Fallback(
    [
        Excel2DataFrame(config.universe),
        Csv2DataFrame(config.universe)
    ],
    callback=LOGGER.warning(universe_cb)
)


pull_overview = Pipe(
    LOGGER.debug(lambda isin: f'Start pulling overview for ISIN "{isin}"'),
    Fork(
        get_etf_overview,
        LOGGER.debug(lambda isin: f'Done pulling overview for ISIN "{isin}"')
    ),
    write_json,
    SideEffect(wait)
)

pull_chart = Pipe(
    LOGGER.debug(lambda isin: f'Start pulling chart for ISIN "{isin}"'),
    Fork(
        Pipe(get_etf_chart, ResetIndex()),
        LOGGER.debug(lambda isin: f'Done pulling chart for ISIN "{isin}"')
    ),
    write_parquet,
    SideEffect(wait)
)

pull_etf = Fork(
    pull_overview,
    pull_chart
)

pull_ticker = Pipe(
    LOGGER.debug(lambda ticker: f'Start pulling ticker "{ticker}"'),
    Fork(
        Pipe(get_yahoo_ticker_history, ResetIndex()),
        LOGGER.debug(lambda ticker: f'Done pulling ticker "{ticker}"')
    ),
    write_parquet,
    SideEffect(wait)
)


load_universe = Pipe(
    LOGGER.info('Loading Universe'),
    read_universe,
    AsType('str'),
    LOGGER.debug('Done loading Universe'),
    Fork(
        ColumnSelector(config.cols.isin),
        Pipe(
            LOGGER.debug('Saving Universe'),
            Drop(config.cols.name, errors='ignore'),
            write_overview,
            LOGGER.info('Done saving Universe')
        )
    )
)


pull_etfs = Pipe(
    LOGGER.info('Start pulling ETFs'),
    LOGGER.debug(lambda xs: f'Processing {len(xs)} ISINs'),
    Map(Safe(pull_etf), wrapper=list, flat=True),
    Map(lambda error: CALLBACK.error(error.message), flat=True),
    LOGGER.info('Done pulling ETFs')
)

pull_tickers = Pipe(
    LOGGER.info('Start pulling Yahoo tickers'),
    config.etl.tickers,
    LOGGER.debug(lambda xs: f'Processing {len(xs)} ticker(s)'),
    Map(Safe(pull_ticker), wrapper=list, flat=True),
    Map(lambda error: CALLBACK.error(error.message), flat=True),
    LOGGER.info('Done pulling Yahoo tickers'),
)


extract = Pipe(
    LOGGER.info('Starting step "pull"'),
    Fork(
        pull_tickers,
            Pipe(load_universe, pull_etfs)
    ),
    LOGGER.info('Done with step "pull"')
)
