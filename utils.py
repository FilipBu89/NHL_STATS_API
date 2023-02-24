"""Module storing few generic functions for running a program."""
import functools
import itertools
import time
from typing import Callable, Any
import aiohttp
from aiohttp import ClientSession
from pathlib import Path
import asyncio
import keyword
from collections import abc

# path to files directory
FILES_DIR = Path().cwd() / "files"


async def download_one(session: ClientSession, url: str, filename: str, subfolder: str) -> str:
    """Get data from specific API endpoint and save data file to a local directory.

    NOTES
    -----
    save_json() is blocking function, and therefore we must create a new thread within the loop.

    :param session: ClientSession object representing a session on which asynchronous requests will run
    :param url: URL for getting data from API
    :param filename: name of the file with downloaded data
    :param subfolder: name of the sub-folder, where downloaded files should be stored

    :return: filename (for convenience, when showing results)
    """
    data = await fetch_data(session, url)
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, save_json, data, filename.lower() + ".json", subfolder)
    return filename


def save_json(data: bytes, filename: str, subfolder: str) -> None:
    """Small function for saving downloaded data.

    :param data:
    :param filename: name of the file with downloaded data
    :param subfolder: name of the sub-folder, where downloaded files should be stored

    :return: None
    """
    path: Path = FILES_DIR / subfolder / filename
    with open(path, "wb") as fh:
        fh.write(data)


def async_timed():
    """Decorator for timing functions."""
    def wrapper(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapped(*args, **kwargs) -> Any:
            print(f'starting {func} with args {args} {kwargs}')
            start = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                end = time.time()
                total = end - start
                print(f'finished {func} in {total:.4f} second(s)')
        return wrapped
    return wrapper


@async_timed()
async def fetch_data(session: ClientSession, url: str, timeout: float = 5) -> bytes:
    """Asynchronous function for getting data from request.

    :param session: ClientSession object representing a session on which asynchronous requests will run
    :param url: URL for getting data from API
    :param timeout: limit for getting request response in seconds

    :return: bytes response from request
    """
    request_timeout = aiohttp.ClientTimeout(total=timeout)
    async with session.get(url, timeout=request_timeout) as response:
        data = await response.read()
        return data


@async_timed()
async def fetch_files(urls: list, filenames: list, subfolder: str) -> None:
    """

    :param urls: list of URLs for getting data from API
    :param filenames: list of filenames for downloaded data
    :param subfolder: name of the sub-folder, where downloaded files should be stored

    :return: None
    """
    subfolder_iter = itertools.repeat(subfolder, len(urls))
    connector = aiohttp.TCPConnector(limit_per_host=10000)
    async with ClientSession(connector=connector) as session:
        tasks = [download_one(session, url, filename, subfolder)
                 for url, filename, subfolder in zip(urls, filenames, subfolder_iter)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        exceptions = [res for res in results if isinstance(res, Exception)]
        success_status_codes = [res for res in results if not isinstance(res, Exception)]

        # print request results
        print(f"All results: [{results}]")
        print(f"Exceptions: [{exceptions}]")
        print(f"Success results: [{success_status_codes}]")


def silence_event_loop_closed(func: Callable) -> Callable:
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


if __name__ == "__main__":
    import doctest
    doctest.testmod()


