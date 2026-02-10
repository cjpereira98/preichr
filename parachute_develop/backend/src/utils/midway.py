import os
import pathlib
import tempfile
import warnings
import http.cookiejar

import requests
from requests_kerberos import HTTPKerberosAuth, OPTIONAL


warnings.simplefilter("ignore")

_HOME_FOLDER: pathlib.Path = pathlib.Path.home()
_MIDWAY_COOKIE_FILENAME: str = os.path.join(_HOME_FOLDER, ".midway", "cookie")


class MidwayUnauthenticatedError(Exception):
    """
    Exception thrown when Midway authentication fails.
    """

    def __init__(self):
        message_1: str = f"Midway cookies from {_MIDWAY_COOKIE_FILENAME} either not found, invalid, or expired."
        message_2: str = "Try running `mwinit -s --aea` to get new cookies."
        super().__init__(f"{message_1} {message_2}")


def _write_temp_file(temp_file: tempfile._TemporaryFileWrapper, line: str) -> None:
    if line.startswith("#HttpOnly_"):
        temp_file.write(line[10:])
    else:
        temp_file.write(line)


def _get_midway_cookies() -> http.cookiejar.MozillaCookieJar:
    """
    Load Midway cookies from a local file.

    :return: cookie jar object loaded with Midway cookies
    :raises MidwayUnauthenticatedError: If there's an issue loading the cookies
    """
    try:
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            with open(_MIDWAY_COOKIE_FILENAME) as midway_file:
                for line in midway_file:
                    _write_temp_file(temp_file, line)
            temp_file.flush()
            cookies: http.cookiejar.MozillaCookieJar = http.cookiejar.MozillaCookieJar(
                temp_file.name)
            cookies.load(ignore_discard=True, ignore_expires=True)
    except Exception:
        raise MidwayUnauthenticatedError()
    else:
        return cookies
    finally:
        os.remove(temp_file.name)


def amzn_requests(url: str, method: str = "get", **kwargs) -> requests.Response:
    """
    Send an HTTP request with Kerberos authentication and Midway cookies.

    :param url: The URL to send the request to.
    :param method: The HTTP method to use (default: "get").
    :param kwargs: Additional arguments to pass to `requests.Session.request`.
    :return: The response from the HTTP request.
    """
    session: requests.Session = requests.Session()
    kerberos_auth: HTTPKerberosAuth = HTTPKerberosAuth(
        mutual_authentication=OPTIONAL)
    mw_cookies: http.cookiejar.MozillaCookieJar = _get_midway_cookies()
    return session.request(
        method,
        url,
        auth=kerberos_auth,
        cookies=mw_cookies,
        verify=False,
        **kwargs
    )  # type: ignore
