import aiohttp


async def get(url, as_json=False, *args, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, *args, **kwargs) as r:

            if r.status != 200:
                if as_json:
                    return None, None

                return None

            if as_json:
                return r, await r.json(content_type=None)

            return await r.read()
