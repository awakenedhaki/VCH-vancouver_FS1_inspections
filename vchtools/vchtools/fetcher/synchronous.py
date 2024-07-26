import json
import logging
import requests

from time import sleep
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from typing import Iterable, Generator, List, Dict, Any, Tuple, Callable


class APIHandler(object):
    """A class for handling API requests.

    Args:
        url (str): The base URL of the API.
        method (str): The HTTP method to use for the requests.
        headers (dict): The headers to include in the requests.
        n_attempts (int): The number of retry attempts for failed requests.
        throttle (float): The time to wait between requests in seconds.

    Attributes:
        url (str): The base URL of the API.
        method (str): The HTTP method to use for the requests.
        headers (dict): The headers to include in the requests.
        n_attempts (int): The number of retry attempts for failed requests.
        throttle (float): The time to wait between requests in seconds.
        session (requests.Session): The session object for making requests.

    Methods:
        __enter__(): Enter method for using the class as a context manager.
        __exit__(exc_type, exc_val, exc_tb): Exit method for cleaning up resources.
        fetch_all(ids, start, finish): Fetches inspection reports for a range of IDs.
        fetch(id): Fetches the inspection report for a specific ID.
    """

    def __init__(self, url, method, headers, n_attempts, timeout, throttle):
        self.url = url
        self.headers = headers
        self.method = method
        self.n_attempts = n_attempts
        self.throttle = throttle
        self.timeout = timeout
        self.session = None

    def __enter__(self):
        self.session = requests.Session()
        self.session.headers = self.headers

        retries = Retry(
            total=self.n_attempts,
            backoff_factor=self.throttle,
            allowed_methods=[self.method],
            status_forcelist=[500, 502, 503, 504],
        )

        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.session.close()

    def fetch_all(
        self, ids: Iterable[str]
    ) -> Generator[Dict[str, List[Dict[str, Any]]], None, None]:
        """Fetches data for multiple IDs.

        Args:
            ids (iterable): An iterable containing the IDs to fetch data for.

        Yields:
            dict: A dictionary containing the fetched data for each ID.
        """
        for id in ids:
            yield {id: list(self.fetch(id=id))}
            sleep(self.throttle)

    def fetch_ranged(
        self, ids: List[str], start: int, finish: int
    ) -> Generator[Dict[str, List[Dict[str, Any]]], None, None]:
        """Fetches records within a specified range.

        Args:
            ids (list): A list of record IDs.
            start (int): The starting index of the range (inclusive).
            finish (int): The ending index of the range (exclusive).

        Yields:
            dict: The fetched records within the specified range.
        """
        logging.info(f"Fetching records in range: [{start}, {finish}).")
        yield from self.fetch_all(ids[start:finish])

    def fetch(self, id: str) -> Generator[Dict[str, Any], None, None]:
        """Fetches the inspection report for a specific ID.

        Args:
            id (str): The ID.

        Yields:
            dict: The JSON response for the ID.

        Raises:
            requests.exceptions.HTTPError: If an HTTP error occurs.
            requests.exceptions.ConnectionError: If a connection error occurs.
            requests.exceptions.Timeout: If a timeout error occurs.
            requests.exceptions.RequestException: If a general request error occurs.
            requests.exceptions.ChunkedEncodingError: If a chunked encoding error occurs.
        """
        try:
            status_code, data = self._submit_request(id)
            yield data
            logging.info(f"Successfully fetched data for ID: {id}")
        except requests.exceptions.HTTPError as err:
            if status_code == 429:
                logging.error(f"Rate limit exceeded: {data} - ID: {id}")
            else:
                logging.error(f"HTTP error occurred: {err} - ID: {id}")
        except requests.exceptions.ConnectionError as err:
            logging.error(f"Connection error occurred: {err} - ID: {id}")
        except requests.exceptions.Timeout as err:
            logging.error(f"Timeout error occurred: {err} - ID: {id}")
        except requests.exceptions.RequestException as err:
            logging.error(f"Error fetching data: {err} - ID: {id}")
        except requests.exceptions.ChunkedEncodingError as err:
            logging.error(f"Chunked Encoding Error: {err} - ID: {id}")

    def _submit_request(self, id):
        raise NotImplementedError("Subclasses must implement this method.")

    def _build_url(self, id):
        raise NotImplementedError("Subclasses must implement this method.")


class GETRequestHandler(APIHandler):
    """Handles GET requests to the API.

    Args:
        url (str): The base URL of the API.
        headers (dict): The headers to be included in the request.
        n_attempts (int): The number of attempts to make the request.
        throttle (float): The time to wait between requests in seconds.

    Attributes:
        url (str): The base URL of the API.
        method (str): The HTTP method of the request.
        headers (dict): The headers to be included in the request.
        n_attempts (int): The number of attempts to make the request.
        throttle (float): The time to wait between requests in seconds.
        session (requests.Session): The session object for making HTTP requests.

    Methods:
        _build_url: Builds the complete URL for the request.
        _submit_request: Submits the request and returns the response.
    """

    def __init__(self, url, headers, n_attempts, timeout, throttle):
        super().__init__(url, "GET", headers, n_attempts, timeout, throttle)

    def _build_url(self, id: str) -> str:
        """Builds the complete URL for the request.

        Args:
            id (str): The ID to be included in the URL.

        Returns:
            str: The complete URL.
        """
        return self.url % id

    def _submit_request(self, id: str) -> Tuple[int, Dict[str, Any]]:
        """Submits the request and returns the response.

        Args:
            id (str): The ID to be included in the URL.

        Returns:
            tuple: A tuple containing the status code and the JSON response.

        Raises:
            requests.HTTPError: If the response status code is not successful.
        """
        with self.session.request(
            method=self.method, url=self._build_url(id), timeout=self.timeout
        ) as response:
            response.raise_for_status()
            return response.status_code, response.json()


class POSTRequestHandler(APIHandler):
    """Handles POST requests to the API.

    Args:
        url (str): The URL to send the POST request to.
        headers (dict): The headers to include in the request.
        n_attempts (int): The number of attempts to make for the request.
        throttle (float): The time to wait between each request attempt.

    Attributes:
        custom_payload (callable): A function that generates a custom payload for the request.

    Methods:
        set_custom_payload: Sets a custom payload function for the request handler.
        _build_payload: Builds the payload for the request.
        _submit_request: Submits the request and returns the response.
    """

    def __init__(self, url, headers, n_attempts, timeout, throttle):
        super().__init__(url, "POST", headers, n_attempts, timeout, throttle)
        self.custom_payload = None

    def set_custom_payload(self, custom_payload: Callable[[str], str]) -> None:
        """Sets a custom payload function for the request handler.

        Args:
            custom_payload (callable): A function that generates a custom payload for the request.
        """
        self.custom_payload = custom_payload

    def _build_payload(self, id: str) -> Dict[str, str]:
        """Builds the payload for the request.

        Args:
            id (str): The ID to include in the payload.

        Returns:
            str: The payload as a JSON string.
        """
        if self.custom_payload is not None:
            return self.custom_payload(id)
        else:
            return json.dumps({"id": id})

    def _submit_request(self, id: str) -> Tuple[int, Dict[str, Any]]:
        """Submits the request and returns the response.

        Args:
            id (str): The ID to include in the request.

        Returns:
            tuple: A tuple containing the status code and the response JSON.

        Raises:
            HTTPError: If the request fails.
        """
        with self.session.request(
            method=self.method,
            url=self.url,
            data=self._build_payload(id),
            timeout=self.timeout,
        ) as response:
            response.raise_for_status()
            return response.status_code, response.json()
