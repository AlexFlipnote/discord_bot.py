ballresponse = [
  'Yes', 'No', 'Take a wild guess...', 'Very doubtful',
  'Sure', 'Without a doubt', 'Most likely', 'Might be possible',
  "You'll be the judge", 'no... (╯°□°）╯︵ ┻━┻', 'no... baka',
  'senpai, pls no ;-;'
]

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'extract_flat': True,
    'yesplaylist': True,
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}

ytdl_noplaylist = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': True,
    'quiet': False,
    'no_warnings': True,
    'default_search': 'auto',
    'noplaylist': True,
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}

ytdl_aria = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'nocheckcertificate': True,
    'logtostderr': True,
    'quiet': True,
    'default_search': 'auto',
    'noplaylist': True,
    'external_downloader': 'aria2c',
    'external_downloader_args': ['-q', '--min-split-size', '1M', '--max-connection-per-server', '16', '--split', '16',
                                 '--max-concurrent-downloads', '16'],
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}
