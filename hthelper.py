from collections import namedtuple
from http import HTTPStatus
import mimetypes
import os
from pathlib import Path
from typing import NamedTuple
from urllib.parse import unquote

from datetime import datetime


class HTTPhelper:
    version = "HTTP/1.0"
    servername = "OTUServer"
    headers = ["Date", "Server", "Content-Length", "Content-Type", "Connection"]
    request = namedtuple(
        "Request", ["method", "address", "version", "query_string"], defaults=(None,)
    )


def make_heads(**kwargs) -> str:
    """
    kwargs expected:
    * length - len(<content>)
    * type - Path('file.suff').suffix()
    """
    dct = {h: "" for h in HTTPhelper.headers}
    dct["Date"] = httpdate()
    dct["Server"] = HTTPhelper.servername
    dct["Content-Length"] = kwargs.get("length", "")
    file = kwargs.get("file")
    if file:
        dct["Content-Type"] = (
            mimetypes.guess_type(kwargs.get("file"))[0] or "text/plain"
        )
    dct["Connection"] = "close"
    result_string = "\r\n".join([f"{h}: {v}" for h, v in dct.items() if v])
    result_string += "\r\n"
    return bytes(result_string.encode("utf-8"))


def make_answer(
    code: HTTPStatus, file: Path or None = None, method: str or None = None
) -> bytes:
    """
    Cook HTTP-answer with provided args.
    """
    string = f"{HTTPhelper.version} {code.value} {code.phrase}"
    lead = bytes(string.encode("utf-8"))
    if not code == 200 or not file:
        headers = make_heads()
        return b"\r\n".join((lead, headers))
    length = os.path.getsize(file)
    headers = make_heads(length=length, file=file)
    if method == "GET":
        with open(file, "rb") as f:
            bytes_read = f.read()
        return b"\r\n".join((lead, headers, bytes_read))
    elif method == "HEAD":  # only headers without content
        headers += b"\r\n"
        return b"\r\n".join((lead, headers))


def get_request(arg: str) -> NamedTuple or None:
    splitted_first_string = arg.split("\r\n")[0].split()
    if len(splitted_first_string) != 3:
        raise ValueError("Bad request")
    method = splitted_first_string[0]
    if method not in ("GET", "HEAD"):
        raise ValueError(f"Ansupported method {method}")
    address = unquote(splitted_first_string[1])
    version = splitted_first_string[2]
    if "?" in address:
        address, query_string = address.split("?")
        return HTTPhelper.request(method, address, version, query_string)
    return HTTPhelper.request(method, address, version)


def httpdate(dt: datetime = datetime.now()) -> str:
    """
    Return a string representation of a date according to RFC 1123
    (HTTP/1.1)
    """
    weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
    month = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ][dt.month - 1]
    string = "%s, %02d %s %04d %02d:%02d:%02d GMT" % (
        weekday,
        dt.day,
        month,
        dt.year,
        dt.hour,
        dt.minute,
        dt.second,
    )
    return string
