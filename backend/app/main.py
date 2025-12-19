from fastapi import FastAPI

from app.api.v1 import users as route_users
from app.db.session import engine, Base
from app.db.models import users as db_users

app = FastAPI(
    title="GeoTrackr API",
    version="0.1.0"
)

app.include_router(route_users.router, prefix="/api/users", tags=["users"])

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "GeoTrackr FastAPI backend is running"}

from bs4 import BeautifulSoup
import requests
import json
from app.db.session import SessionLocal
from app.parser import parse_and_create_duel

@app.post("/process-game")
async def process_game(game_id: str):
    response = requests.get(f"https://www.geoguessr.com/duels/{game_id}", cookies={"_ncfa": "gTKqont5+cRsh65xWdULEQytY8lYsJOf8GrV/L/mtds=hAa398nwEsKh/1HqykeLhExyTQTWQFaEXCompvjBivpDhCGj6OH5qsH/KroahHr+zRiGuc+y//cIgjQpmrSSPANTJ5cqbai+qWsBIef+MfI="})
    soup = BeautifulSoup(response.text, "html.parser")
    script_tag = soup.find("script", id="__NEXT_DATA__")

    if not script_tag:
        raise ValueError("No <script id='__NEXT_DATA__'> found in page")

    duel_data = json.loads(script_tag.string)["props"]["pageProps"]["game"]

    with SessionLocal() as db:
        duel = parse_and_create_duel(db, duel_data)
        print(f"✅ Duel {duel.id} created successfully")
    return {"message": f"Processing game at {game_id}"}


from sqlalchemy.orm import joinedload
from app.db.models.duels import Map, SoloDuel, DuelRound
from sqlalchemy.orm import Session
from app.schemas.duels import SoloDuelSchema
from app.schemas.users import UserSchema

def get_solo_duel_full(db: Session):
    return (
        db.query(SoloDuel)
        .options(
            joinedload(SoloDuel.map),
            joinedload(SoloDuel.rounds)
                .joinedload(DuelRound.panorama),
            joinedload(SoloDuel.rounds)
                .joinedload(DuelRound.guesses),
            joinedload(SoloDuel.player1),
            joinedload(SoloDuel.player2),
        )
        .first()
    )

def get_player(db: Session):
    return db.query(db_users.User).first()

@app.get("/test", response_model=UserSchema)
async def test_endpoint():
    with SessionLocal() as db:
        player = get_player(db)
        print(player.duels)
    return player

@app.get("/users", response_model=list[UserSchema])
async def get_users(username: str | None = None, limit: int = 10, offset: int = 0):
    with SessionLocal() as db:
        query = db.query(db_users.User)
        if username:
            query = query.filter(db_users.User.username.ilike(f"%{username}%"))
        users = query.limit(limit).offset(offset).all()
    return users

@app.get("/users/{user_id}", response_model=UserSchema)
async def get_user(user_id: str):
    with SessionLocal() as db:
        user = db.query(db_users.User).filter(db_users.User.id == user_id).first()
    return user

@app.get("/users/{user_id}/duels", response_model=list[SoloDuelSchema])
async def get_user_duels(user_id: str, limit: int = 10, offset: int = 0):
    with SessionLocal() as db:
        user = db.query(db_users.User).filter(db_users.User.id == user_id).first()
        duels = (
            db.query(SoloDuel)
            .options(
                joinedload(SoloDuel.map),
                joinedload(SoloDuel.rounds)
                    .joinedload(DuelRound.panorama),
                joinedload(SoloDuel.rounds)
                    .joinedload(DuelRound.guesses),
                joinedload(SoloDuel.player1),
                joinedload(SoloDuel.player2),
                joinedload(SoloDuel.elo_histories),
            )
            .filter(
                (SoloDuel.player1_id == user_id) | (SoloDuel.player2_id == user_id)
            )
            .order_by(SoloDuel.start_time.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
    for duel in duels:
        duel.rounds.sort(key=lambda r: r.round_number)
    return duels


@app.get("/users/{user_id}/ranking")
async def get_user_ranking(user_id: str):
    with SessionLocal() as db:
        user = db.query(db_users.User).options(joinedload(db_users.User.elo_histories)).filter(db_users.User.id == user_id).first()
        ranking_data = [
            {
                "elo": elo_history.elo_after,
                "timestamp": elo_history.datetime,
            }
            for elo_history in user.elo_histories
        ]
    return ranking_data