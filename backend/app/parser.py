import uuid
from sqlalchemy.orm import Session
from app.db.models.duels import Map, Panorama, Team, SoloDuel, DuoDuel, DuelRound, DuelGuess, EloHistory
from app.db.models.users import User


def parse_and_create_duel(db: Session, data: dict):
    print(data)
    game_type = data.get("gameType", "").lower()
    if game_type == "teamDuels":
        print("Parsing Duo Duel is not implemented yet.")
        return None
    
    map_data = data["options"]["map"]
    map_id = map_data["slug"]
    map_obj = db.query(Map).filter(Map.id == map_id).first()
    if not map_obj:
        map_obj = Map(id=map_id, name=map_data["name"])
        db.add(map_obj)


    players = [data["teams"][0]["players"][0], data["teams"][1]["players"][0]]
    player1_id, player2_id = players[0]["playerId"], players[1]["playerId"]

    winning_team_id = data.get("result", {}).get("winningTeamId")
    if winning_team_id:
        if winning_team_id == data["teams"][0]["id"]:
            winner_id = data["teams"][0]["players"][0]["playerId"]
            loser_id = data["teams"][1]["players"][0]["playerId"]
        elif winning_team_id == data["teams"][1]["id"]:
            winner_id = data["teams"][1]["players"][0]["playerId"]
            loser_id = data["teams"][0]["players"][0]["playerId"]
    
    for player in players:
        user = db.query(User).filter(User.id == player["playerId"]).first()
        if not user:
            user = User(
                id=player["playerId"],
                username=player.get("nick"),
                country_code=player.get("countryCode"),
                rating=player.get("rating", 0),
                avatar_url=player.get("avatar").get("fullBodyPath"),
                pin_url=player.get("pinUrl"),
            )
            db.add(user)
        else:
            user.username = player.get("nick", user.username)
            user.country_code = player.get("countryCode", user.country_code)
            user.rating = player.get("rating", user.rating)
            user.avatar_url = player.get("avatar").get("fullBodyPath", user.avatar_url)
            user.pin_url = player.get("pinUrl", user.pin_url)

    duel = SoloDuel(
        id=data["gameId"],
        mode=data["gameType"],
        map_id=map_obj.id,
        start_time=data["rounds"][0]["startTime"] if data["rounds"] else 0,
        ranked=data["isRated"],
        player1_id=player1_id,
        player2_id=player2_id,
        winner_id=winner_id,
        loser_id=loser_id,
    )
    db.add(duel)
    db.flush()

    if data["isRated"]:
        for player in players:
            user = db.query(User).filter(User.id == player["playerId"]).first()
            elo_change = player.get("progressChange", {}).get("rankedSystemProgress", {})
            if user and elo_change is not None:
                elo_history = EloHistory(
                    user_id=user.id,
                    duel_id=duel.id,
                    datetime=data["rounds"][0]["startTime"] if data["rounds"] else 0,
                    elo_before=elo_change.get("ratingBefore"),
                    elo_after=elo_change.get("ratingAfter"),
                )
                db.add(elo_history)
                
    for round_data in data["rounds"]:
        pano = round_data["panorama"]
        pano_id = pano["panoId"]

        pano_obj = db.query(Panorama).filter(Panorama.id == pano_id).first()
        if not pano_obj:
            pano_obj = Panorama(
                id=pano_id,
                lat=pano["lat"],
                lng=pano["lng"],
                country_code=pano.get("countryCode"),
                heading=pano.get("heading"),
                pitch=pano.get("pitch"),
                zoom=pano.get("zoom"),
            )
            db.add(pano_obj)

        team1 = data["teams"][0]["roundResults"]
        team2 = data["teams"][1]["roundResults"]

        team1_round = next((r for r in team1 if r["roundNumber"] == round_data["roundNumber"]), None)
        team2_round = next((r for r in team2 if r["roundNumber"] == round_data["roundNumber"]), None)

        round_guesses = []
        for team_data in data["teams"]:
            for player in team_data["players"]:
                for guess in player.get("guesses", []):
                    if guess["roundNumber"] != round_data["roundNumber"]:
                        continue
                    round_guesses.append({
                        "player_id": player["playerId"],
                        "lat": guess["lat"],
                        "lng": guess["lng"],
                        "distance": guess["distance"],
                        "score": guess.get("score", 0),
                    })

        if not round_guesses:
            continue

        round_obj = DuelRound(
            id=str(uuid.uuid4()),
            duel_id=duel.id,
            round_number=round_data["roundNumber"],
            panorama_id=pano_obj.id,
            player1_hp_before=team1_round["healthBefore"] if team1_round else None,
            player1_hp_after=team1_round["healthAfter"] if team1_round else None,
            player2_hp_before=team2_round["healthBefore"] if team2_round else None,
            player2_hp_after=team2_round["healthAfter"] if team2_round else None,
        )
        db.add(round_obj)

        for g in round_guesses:
            guess_obj = DuelGuess(
                round_id=round_obj.id,
                player_id=g["player_id"],
                lat=g["lat"],
                lng=g["lng"],
                distance=g["distance"],
                score=g["score"],
            )
            db.add(guess_obj)

    db.commit()
    db.refresh(duel)
    return duel
