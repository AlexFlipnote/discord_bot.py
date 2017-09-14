from youtube_dl import YoutubeDL
from assets import lists

"""
    License: MIT
    Originally By Rapptz. Modified and Adapted By Joshwoo70. Further Tweaks thanks to AlexFlipnote
"""

ytdlnpl = YoutubeDL(lists.ytdl_noplaylist)
ytdl = YoutubeDL(lists.ytdl_format_options)
ytdlaria = YoutubeDL(lists.ytdl_aria)


def exinfo(url, playlist=False):
    if playlist:
        return ytdl.extract_info(url, download=False)
    else:
        return ytdlnpl.extract_info(url, download=False)
