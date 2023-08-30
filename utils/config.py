from __future__ import annotations
from typing import Any, TYPE_CHECKING, Optional

import re

from dataclasses import dataclass
from dotenv import dotenv_values

if TYPE_CHECKING:
    from typing_extensions import Self

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

    owner_guild_id: Optional[int]
    streaming_status_url: Optional[str]

    @classmethod
    def from_dict(cls, **kwargs: Any) -> Self:
        """Create a Config object from a dictionary."""
        kwargs_overwrite = {}

        for k, v in kwargs.items():
            new_key = k.lower()

            if v.isdigit():
                kwargs_overwrite[new_key] = int(v)
            else:
                kwargs_overwrite[new_key] = v

        return cls(**kwargs_overwrite)

    @classmethod
    def from_env(cls, filename: str = ".env") -> Self:
        """Create a Config object from a .env file."""
        return cls.from_dict(**dotenv_values(filename))
