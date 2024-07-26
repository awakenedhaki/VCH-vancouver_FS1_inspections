import logging

from typing import List, Callable, Generator, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from vchtools.fetcher.synchronous import GETRequestHandler, POSTRequestHandler


class ThreadedRequestHandlerMixin(object):
    """Mixin class for executing requests in a threaded manner.

    This class provides a method `execute_requests_threaded` to execute multiple requests
    concurrently using a thread pool. It uses the `ThreadPoolExecutor` class from the
    `concurrent.futures` module.

    Attributes:
        None

    Methods:
        execute_requests_threaded: Executes multiple requests concurrently using a thread pool.
    """

    def execute_requests_threaded(
        self,
        ids: List[str],
        worker_func: Callable[[str], Generator[Dict[str, Any], None, None]],
        n_workers: int,
    ) -> Generator[Dict[str, Any], None, None]:
        """Executes multiple requests concurrently using a thread pool.

        Args:
            ids (list): A list of IDs to be requested.
            worker_func (callable): The worker function that will be called for each task.
            n_workers (int): The number of worker threads to use.

        Yields:
            The results of the worker function for each ID.
        """
        with ThreadPoolExecutor(max_workers=n_workers) as executor:
            futures = {executor.submit(worker_func, id): id for id in ids}
            for future in as_completed(futures):
                task = futures[future]
                try:
                    yield from future.result()
                except Exception as exc:
                    logging.error(f"Error processing task {task}: {exc}")


class ThreadedGETRequestHandler(GETRequestHandler, ThreadedRequestHandlerMixin):
    """A threaded GET request handler that fetches records in parallel.

    This class extends the GETRequestHandler and ThreadedRequestHandlerMixin classes.
    It provides methods for fetching records in parallel using multiple worker threads.

    Attributes:
        None

    Methods:
        fetch_all_threaded: Fetches all records in parallel using multiple worker threads.
        fetch_ranged_threaded: Fetches a range of records in parallel using multiple worker threads.
    """

    def fetch_all_threaded(
        self, ids: List[str], n_workers: int
    ) -> Generator[Dict[str, Any], None, None]:
        """Fetches all records in a threaded manner.

        Args:
            ids (list): A list of record IDs to fetch.
            n_workers (int): The number of worker threads to use.

        Yields:
            A dictionary containing the fetched data for each ID.
        """
        return self.execute_requests_threaded(ids, self.fetch, n_workers)

    def fetch_ranged_threaded(
        self, ids: List[str], start: int, finish: int, n_workers: int
    ) -> Generator[Dict[str, Any], None, None]:
        """Fetches a range of records in parallel using multiple worker threads.

        Args:
            ids (list): A list of record IDs.
            start (int): The starting index of the range.
            finish (int): The ending index of the range.
            n_workers (int): The number of worker threads to use.

        Yields:
            The fetched records within the specified range.
        """
        logging.info(f"Fetching records in range: [{start}, {finish}).")
        sliced_ids = ids[start:finish]
        yield from self.fetch_all_threaded(sliced_ids, n_workers)


class ThreadedPOSTRequestHandler(POSTRequestHandler, ThreadedRequestHandlerMixin):
    """A class that handles threaded POST requests.

    This class inherits from POSTRequestHandler and ThreadedRequestHandlerMixin.

    Attributes:
        None

    Methods:
        fetch_all_threaded: Fetches all records in a threaded manner.
        fetch_ranged_threaded: Fetches records within a specified range in a threaded manner.
    """

    def fetch_all_threaded(
        self, ids: List[str], n_workers: int
    ) -> Generator[Dict[str, Any], None, None]:
        """Fetches all records in a threaded manner.

        Args:
            ids (list): A list of record IDs to fetch.
            n_workers (int): The number of worker threads to use.

        Yields:
            A dictionary containing the fetched data for each ID.
        """
        return self.execute_requests_threaded(ids, self.fetch, n_workers)

    def fetch_ranged_threaded(
        self, ids: List[str], start: int, finish: int, n_workers: int
    ) -> Generator[Dict[str, Any], None, None]:
        """Fetches records within a specified range in a threaded manner.

        Args:
            ids (list): A list of record IDs to fetch.
            start (int): The starting index of the range.
            finish (int): The ending index of the range.
            n_workers (int): The number of worker threads to use.

        Yields:
            The fetched records within the specified range.
        """
        logging.info(f"Fetching records in range: [{start}, {finish}).")
        sliced_ids = ids[start:finish]
        yield from self.fetch_all_threaded(sliced_ids, n_workers)
