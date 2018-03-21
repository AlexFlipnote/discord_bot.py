"""
Copyright (C) Martmists and Alexflipnote - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Martmists <legal@martmists.com> and
           Alexflipnote <alexander@samuels1.no>, June 2017

Licensed to xelA/discord_bot.py
"""

import asyncio
import aiohttp

from utils import cache


# Removes the aiohttp ClientSession instance warning.


class HTTPSession(aiohttp.ClientSession):
    """abstract class for aiohttp."""
    def __init__(self, loop=None):
        super().__init__(loop=loop or asyncio.get_event_loop())

    def __del__(self):
        """
        closes the ClientSession instance
        cleanly when the instance is deleted.

        Useful for things like when the interpreter closes.

        This would be perfect if discord.py had this as well. :thinking:
        """
        if not self.closed:
            self.close()


session = HTTPSession()


@cache.async_cache()
async def query(url, method="get", res_method="text", *args, **kwargs):
    async with getattr(session, method.lower())(url, *args, **kwargs) as res:
        return await getattr(res, res_method)()


async def get(url, *args, **kwargs):
    return await query(url, "get", *args, **kwargs)


async def post(url, *args, **kwargs):
    return await query(url, "post", *args, **kwargs)
