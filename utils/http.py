import aiohttp

from utils import cache


# Removes the aiohttp ClientSession instance warning.
class HTTPSession(aiohttp.ClientSession):
    """ Abstract class for aiohttp. """

    def __del__(self):
        if not self.closed:
            self.close()


session = HTTPSession()


@cache.async_cache()
async def query(url: str, method: str = "get", res_method: str = "text", *args, **kwargs):
    async with getattr(session, method.lower())(url, *args, **kwargs) as res:
        return await getattr(res, res_method)()


async def get(url: str, *args, **kwargs):
    return await query(url, "get", *args, **kwargs)


async def post(url: str, *args, **kwargs):
    return await query(url, "post", *args, **kwargs)
