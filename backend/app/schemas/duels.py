from pydantic import BaseModel
from typing import List, Optional

from app.schemas.users import UserSchema

class PanoramaSchema(BaseModel):
    id: str
    lat: float
    lng: float
    country_code: Optional[str]
    heading: Optional[float]
    pitch: Optional[float]
    zoom: Optional[int]

    class Config:
        orm_mode = True


class DuelGuessSchema(BaseModel):
    round_id: str
    player_id: str
    lat: float
    lng: float
    distance: float
    score: int

    class Config:
        orm_mode = True


class DuelRoundSchema(BaseModel):
    id: str
    round_number: int
    player1_hp_before: int
    player1_hp_after: int
    player2_hp_before: int
    player2_hp_after: int
    panorama: PanoramaSchema
    guesses: List[DuelGuessSchema]

    class Config:
        orm_mode = True


class MapSchema(BaseModel):
    id: str
    name: str

    class Config:
        orm_mode = True


class EloHistorySchema(BaseModel):
    duel_id: str
    user_id: str
    datetime: int
    elo_before: int
    elo_after: int

    class Config:
        orm_mode = True

class SoloDuelSchema(BaseModel):
    id: str
    mode: str
    start_time: int
    player1_elo_change: Optional[int]
    player2_elo_change: Optional[int]
    winner_id: str
    loser_id: str
    ranked: bool
    map: MapSchema
    rounds: List[DuelRoundSchema]
    player1: UserSchema
    player2: UserSchema
    elo_histories: List[EloHistorySchema]

    class Config:
        orm_mode = True
