import aiohttp
import json

from aiohttp.client_exceptions import ContentTypeError


class HTTPResponse:
    def __init__(
        self, status: int, response: str,
        res_method: str, headers: dict[str, str]
    ):
        self.status = status
        self.response = response
        self.res_method = res_method
        self.headers = headers

    def __repr__(self) -> str:
        return f"<HTTPResponse status={self.status} res_method='{self.res_method}'>"


async def query(url, method="get", res_method="text", *args, **kwargs) -> HTTPResponse:
    """ Make a HTTP request using aiohttp """
    session = aiohttp.ClientSession()

    async with getattr(session, method.lower())(url, *args, **kwargs) as res:
        try:
            r = await getattr(res, res_method)()
        except ContentTypeError:
            if res_method == "json":
                r = json.loads(await res.text())

        output = HTTPResponse(
            status=res.status,
            response=r,
            res_method=res_method,
            headers=res.headers
        )

    await session.close()
    return output


async def get(url, *args, **kwargs) -> HTTPResponse:
    """ Shortcut for query(url, "get", *args, **kwargs) """
    return await query(url, "get", *args, **kwargs)


async def post(url, *args, **kwargs) -> HTTPResponse:
    """ Shortcut for query(url, "post", *args, **kwargs) """
    return await query(url, "post", *args, **kwargs)
