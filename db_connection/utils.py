from collections import abc
import psycopg2
import functools
import datetime
import traceback as tb
import keyword
import logging
from configparser import ConfigParser
from pathlib import Path
from logging import Logger

# path to files directory
FILES_DIR = Path().cwd().parent / "files"


def get_logger() -> Logger:
    """ """
    # logging set-up
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    logger_format = "%(asctime)s:%(levelname)s:%(message)s"
    formatter = logging.Formatter(logger_format)

    file_handler = logging.FileHandler(f"./logs/my_log_{datetime.date.today()}.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_db_config(filename: Path, section: str = "postgresql") -> dict:
    """Small help function for parsing db config file

    filename: path to db config file
    section: specific section of config file, which is defining scope of the configuration

    :returns: config dictionary; {'host': str, 'database': str, 'user': str, 'password': str}
    """
    # create a parser
    parser = ConfigParser()

    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise ValueError('Section {0} not found in the {1} file'.format(section, filename))

    return db


class MyDBConnectionTransaction:
    """ """
    def __init__(self, configuration_parameters: dict, logger: Logger):
        self.connection = psycopg2.connect(**configuration_parameters)
        self.cursor = self.connection.cursor()
        self.logger = logger

    def __enter__(self):
        """ """
        self.logger.info("Creating new DB connection")
        self.logger.info("Running transaction statements")
        return self.connection, self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ """
        if exc_type is None:
            self.logger.info("Committing session transaction")
            self.connection.commit()
        else:
            self.logger.info("Rolling back session transaction")
            self.connection.rollback()

        # close opened resources
        self.logger.info("Closing DB connection resources")
        self.connection.close()
        self.cursor.close()


class MyDBConnectionFetch:
    """ """
    def __init__(self, configuration_parameters: dict, logger: Logger):
        self.connection = psycopg2.connect(**configuration_parameters)
        self.cursor = self.connection.cursor()
        self.logger = logger

    def __enter__(self):
        """ """
        self.logger.info("Creating new DB connection")
        self.logger.info("Running select statements")
        return self.connection, self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ """
        # close opened resources
        self.logger.info("Closing DB connection resources")
        self.connection.close()
        self.cursor.close()


class FrozenJSON:
    """A read-only facade for navigating a JSON-like object using attribute notation.

    NOTES
    -----
    Re-used from Fluent Python by Luciano Ramalho

    USAGE
    _____
    >>> my_dict = {"player": {"team": "Super Mario", "name": "Luigi"}, "stats": {"matches": 23,"goals": 10, "assists": 8}}
    >>> player = FrozenJSON(my_dict)
    >>> player.stats.matches
    23
    >>> type(player.stats)
    <class 'utils.FrozenJSON'>
    >>> player.player.country
    Traceback (most recent call last):
    ...
    AttributeError: 'FrozenJSON' has no attribute 'country'
    """
    def __new__(cls, arg):
        if isinstance(arg, abc.Mapping):
            return super().__new__(cls)
        elif isinstance(arg, abc.MutableSequence):
            return [cls(item) for item in arg]
        else:
            return arg

    def __init__(self, mapping):
        self.__data = dict(mapping)
        for key, value in mapping.items():
            if keyword.iskeyword(key):
                key += '_'
                self.__data[key] = value

    def __getattr__(self, name):
        if hasattr(self.__data, name):
            return getattr(self.__data, name)
        else:
            try:
                return FrozenJSON(self.__data[name])
            except KeyError as err:
                raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'") from err


def silence_event_loop_closed(func):
    """Custom wrapper function for silencing asyncio runtime error.

    When running asynchronous API requests script might throw a runtime error saying that 'Event loop is closed' even
    after the loop is done running.

    In some cases this can be fixed by using asyncio.get_new_loop().run_until_complete() instead of asyncio.run(),
    however this might not be the case in conjunction with aiohttp library.

    The solution might be using this function as wrapper for replacing the delete method of ProactorBasePipeTransport.

    USAGE
    _____
    >>> from asyncio.proactor_events import _ProactorBasePipeTransport
    >>> _ProactorBasePipeTransport.__del__ = silence_event_loop_closed(_ProactorBasePipeTransport.__del__)
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except RuntimeError as e:
            if str(e) != 'Event loop is closed':
                raise
    return wrapper
