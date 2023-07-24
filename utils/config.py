import re

from dataclasses import dataclass
from dotenv import dotenv_values

re_list: re.Pattern = re.compile(r"\s*,\s*")


@dataclass
class Config:
    """
    This class is used to store the bot's configuration.
    You can load it from a dictionary or from a .env file (recommended).
    By default in this Discord bot template, we use from_env classmethod.

    TODO: Make it support lists from .env
            Does not work as of right now,
            `re_list` is planned for that usage.
    """
    discord_token: str
    discord_owner_ids: list[int]
    discord_join_message: str

    discord_activity_name: str
    discord_activity_type: str
    discord_status_type: str

    discord_guild_id: int = None
    discord_status_url: str = None

    @classmethod
    def from_dict(self, **kwargs) -> "Config":
        """ Create a Config object from a dictionary. """
        kwargs_overwrite = {}

        for k, v in kwargs.items():
            new_key = k.lower()

            if v.isdigit():
                kwargs_overwrite[new_key] = int(v)
            else:
                kwargs_overwrite[new_key] = v

        return Config(**kwargs_overwrite)

    @classmethod
    def from_env(self, filename: str = ".env") -> "Config":
        """ Create a Config object from a .env file. """
        return Config.from_dict(**dotenv_values(filename))
