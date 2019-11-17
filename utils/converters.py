import datetime
import re

from discord.ext import commands

import parsedatetime as pdt


class TimeConverter(commands.Converter):
    """Converter returning a datetime """
    async def convert(self, ctx, argument):
        # Try to get a datetime with parsedatetime
        cal = pdt.Calendar()
        date, code = cal.parseDT(argument)

        if code > 0:
            return date

        # Fallback for simple time format
        tokens = {
            's':  1,             # Seconds
            'm':  60,            # Minutes
            'h':  60*60,         # Hours
            'd':  60*60*24,      # Days
            'w':  60*60*24*7,    # Weeks
            'mo': 60*60*24*30,   # Months
            'y':  60*60*24*365,  # Years
        }
        total = 0
        for x, t in re.findall('(\d+)([a-zA-Z]+)', argument):
            if t not in tokens:
                raise commands.BadArgument(f'`{t}` is not valid time format, choose from (s, m, h, d, w, mo, y)')
            total += tokens[t]*int(x)

        if total == 0:
            raise commands.BadArgument('Please provide a valid time format')
        return datetime.datetime.now()+datetime.timedelta(seconds=total)
