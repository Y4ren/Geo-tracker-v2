from sqlalchemy import Column, String, Integer, BigInteger, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class Map(Base):
    __tablename__ = "maps"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

    solo_duels = relationship("SoloDuel", back_populates="map", cascade="all, delete-orphan")
    duo_duels = relationship("DuoDuel", back_populates="map", cascade="all, delete-orphan")


class Panorama(Base):
    __tablename__ = "panoramas"

    id = Column(String, primary_key=True, index=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    country_code = Column(String, nullable=True)
    heading = Column(Float, nullable=True)
    pitch = Column(Float, nullable=True)
    zoom = Column(Integer, nullable=True)

    rounds = relationship("DuelRound", back_populates="panorama")


class SoloDuel(Base):
    __tablename__ = "solo_duels"

    id = Column(String, primary_key=True, index=True)
    mode = Column(String, nullable=False)
    map_id = Column(String, ForeignKey("maps.id", ondelete="SET NULL"))
    start_time = Column(BigInteger, nullable=False)
    ranked = Column(Boolean, default=False)

    player1_id = Column(String, ForeignKey("users.id"), nullable=False)
    player2_id = Column(String, ForeignKey("users.id"), nullable=False)

    player1_elo_change = Column(Integer, nullable=True)
    player2_elo_change = Column(Integer, nullable=True)
    
    winner_id = Column(String, ForeignKey("users.id"), nullable=False)
    loser_id = Column(String, ForeignKey("users.id"), nullable=False)

    map = relationship("Map", back_populates="solo_duels")
    rounds = relationship("DuelRound", back_populates="duel", cascade="all, delete-orphan")

    player1 = relationship("User", foreign_keys=[player1_id], back_populates="solo_duels_as_player1")
    player2 = relationship("User", foreign_keys=[player2_id], back_populates="solo_duels_as_player2")

    winner = relationship("User", foreign_keys=[winner_id], backref="won_duels")
    loser = relationship("User", foreign_keys=[loser_id], backref="lost_duels")
    elo_histories = relationship("EloHistory", back_populates="duel", cascade="all, delete-orphan")

class EloHistory(Base):
    __tablename__ = "elo_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    duel_id = Column(String, ForeignKey("solo_duels.id"), nullable=False)
    datetime = Column(BigInteger, nullable=False)
    elo_before = Column(Integer, nullable=False)
    elo_after = Column(Integer, nullable=False)

    user = relationship("User", back_populates="elo_histories")
    duel = relationship("SoloDuel", back_populates="elo_histories")


class DuelRound(Base):
    __tablename__ = "duel_rounds"

    id = Column(String, primary_key=True, index=True)
    duel_id = Column(String, ForeignKey("solo_duels.id", ondelete="CASCADE"), nullable=False)
    round_number = Column(Integer, nullable=False)
    panorama_id = Column(String, ForeignKey("panoramas.id", ondelete="SET NULL"), nullable=True)
    player1_hp_before = Column(Integer, nullable=False)
    player1_hp_after = Column(Integer, nullable=False)
    player2_hp_before = Column(Integer, nullable=False)
    player2_hp_after = Column(Integer, nullable=False)


    duel = relationship("SoloDuel", back_populates="rounds")
    panorama = relationship("Panorama", back_populates="rounds")
    guesses = relationship("DuelGuess", back_populates="round", cascade="all, delete-orphan")


class DuelGuess(Base):
    __tablename__ = "duel_guesses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    round_id = Column(String, ForeignKey("duel_rounds.id", ondelete="CASCADE"), nullable=False)
    player_id = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    distance = Column(Float, nullable=False)
    score = Column(Integer, nullable=False)

    round = relationship("DuelRound", back_populates="guesses")


class Team(Base):
    __tablename__ = "teams"

    id = Column(String, primary_key=True)
    player1_id = Column(String, ForeignKey("users.id"))
    player2_id = Column(String, ForeignKey("users.id"))

    player1 = relationship("User", foreign_keys=[player1_id])
    player2 = relationship("User", foreign_keys=[player2_id])

    duels_as_team1 = relationship("DuoDuel", back_populates="team1", foreign_keys="[DuoDuel.team1_id]")
    duels_as_team2 = relationship("DuoDuel", back_populates="team2", foreign_keys="[DuoDuel.team2_id]")


class DuoDuel(Base):
    __tablename__ = "duo_duels"

    id = Column(String, primary_key=True, index=True)
    mode = Column(String, nullable=False)
    map_id = Column(String, ForeignKey("maps.id", ondelete="SET NULL"))
    start_time = Column(BigInteger, nullable=False)
    ranked = Column(Boolean, default=False)
    team1_id = Column(String, ForeignKey("teams.id", ondelete="CASCADE"))
    team2_id = Column(String, ForeignKey("teams.id", ondelete="CASCADE"))

    team1 = relationship("Team", foreign_keys=[team1_id], back_populates="duels_as_team1")
    team2 = relationship("Team", foreign_keys=[team2_id], back_populates="duels_as_team2")
    map = relationship("Map", back_populates="duo_duels")
