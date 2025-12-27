import random
from typing import List
from pydantic import BaseModel, Field, field_validator

class Players(BaseModel):
    players: List[str] = Field(min_length=10, max_length=10)

    @field_validator("players")
    @classmethod
    def no_entry_names(cls, value: List[str]) -> List[str]:
        for name in value:
            if not name.strip():
                raise ValueError("Имена игроков не могут быть пустыми")
        return value


def split_team(players_list: List[str]) -> tuple[List[str], List[str]]:
    random.shuffle(players_list)

    return players_list[:5], players_list[5:]



