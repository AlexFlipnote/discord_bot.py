<p align="center">
  <img alt="discord_bot.py" src="https://i.alexflipnote.dev/MiFAeTE.png" width="750px">
</p>

Do you need more help? Visit my server here: **https://discord.gg/yqb7vATbjH** 🍺

## Requirements
- Python 3.11 and up - https://www.python.org/downloads/

## Useful to always have
Keep [this](https://discordhttp.alexflipnote.dev/) saved somewhere, as this is the docs to discord.http.
All you need to know about the library is defined inside here, even code that I don't use in this example is here.

This code is also made to be as typing friendly as possible with comments and everything.
I recommend having Visual Studio Code with the Python extension installed to help you out with the code.

## How to setup
1. Make a bot [here](https://discordapp.com/developers/applications/me) and grab the token
![Image_Example1](https://i.alexflipnote.dev/f9668b.png)

1. Rename the file **config.json.example** to **config.json**, then fill in the required spots, such as token and owner_id

2. To install what you need, do **pip install -r requirements.txt**<br>
(If that doesn't work, do **python -m pip install -r requirements.txt**)<br>
`NOTE: Use pip install with Administrator/sudo`

3. Start the bot by having the cmd/terminal inside the bot folder and type **python index.py**

4. You're done, enjoy your bot!

## Config
| Key | Description |
| --- | --- |
| `token` | Your bot token from the Developer Portal |
| `owner_id` | Your Discord user ID, used for owner-only commands |
| `playing` | Bot playing status that will appear when bot is running |
| `sync` | Whether to sync the slash commands to Discord when the bot boots |
| `debug` | Optional settings for development, see below |

### Debug mode
In **config.json.example** the debug block is named `debug_OFF`, which means it's turned off.
To turn it on, rename it to `debug`.
- `guild_id`: Only syncs the slash commands to this server, which makes them show up instantly instead of waiting for global commands to update
- `logging`: Set to `true` to print debug logs in the terminal, useful when something isn't working

## FAQ
Q: I don't see my bot on my server!<br>
A: Invite it by using this URL: https://discordapp.com/oauth2/authorize?client_id=CLIENT_ID&scope=bot<br>
Remember to replace **CLIENT_ID** with your bot client ID

Q: There aren't that many commands here...<br>
A: Yes, I will only provide a few commands to get you started, maybe adding more later.

Q: What happened to the discord.py version?<br>
A: I swapped over to my own library, [discord.http](https://discordhttp.alexflipnote.dev/), since I want full control over the code and how it works.
This also made the template a lot simpler, as it's now less about copy-pasting a big bot and more about being an easy tutorial to learn from.
The old discord.py version is still available in the [legacy/discord.py](https://github.com/AlexFlipnote/discord_bot.py/tree/legacy/discord.py) branch, but it will no longer be updated.

Q: Why the beer with the discord logo?<br>
A: Because the framework is made so simple that even a drunk guy can set it up.

# Optional tools
### Ruff and pyright
These two tools help you keep your code clean and catch mistakes before you run the bot.
- **[Ruff](https://docs.astral.sh/ruff/)** is a linter and formatter that checks your code style and finds common bugs.
- **[pyright](https://github.com/microsoft/pyright)** is a type checker that makes sure you're using variables and functions the right way.

Both are already set up in `pyproject.toml`, and most code editors have a plugin for them so they can be integrated with your IDE.
To install them, simply do `pip install ruff pyright` (or `uv sync --extra dev` if you use uv).
```
# Check the code for linting issues
ruff check

# Check the code for typing issues
pyright
```

### PM2
PM2 is an alternative script provided by NodeJS, which will reboot your bot whenever it crashes and keep it up with a nice status. You can install it by doing `npm install -g pm2` and you should be done. Keep in mind that this PM2 file is made to work on my own Linux instance, you might need to change the `interpreter` value.
```
# Start the bot
pm2 start pm2.json

# Tips on common commands
pm2 <command> [name]
  start discord_bot.py    Run the bot again if it's offline
  list                    Get a full list of all available services
  stop discord_bot.py     Stop the bot
  reboot discord_bot.py   Reboot the bot
```

### Docker
Docker is an alternative to run the bot 24/7 and always reboot again whenever it crashed. You can find the install manual [here](https://docs.docker.com/install/). You don't *have* to get it, but if you're used to having Docker, it's available at least.
```
# Build and run the Dockerfile
docker-compose up -d --build

# Tips on common commands
docker-compose <command>
  ps      Check if bot is online or not (list)
  down    Shut down the bot
  reboot  Reboot the bot without shutting it down or rebuilding
  logs    Check the logs made by the bot.
```
