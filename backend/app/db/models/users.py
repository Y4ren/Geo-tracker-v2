from sqlalchemy import Column, Integer, String, ForeignKey, Table
from app.db.session import Base
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    country_code = Column(String, nullable=False)
    rating = Column(Integer, default=0)
    avatar_url = Column(String, nullable=True)
    pin_url = Column(String, nullable=True)

    solo_duels_as_player1 = relationship("SoloDuel", back_populates="player1", foreign_keys="[SoloDuel.player1_id]")
    solo_duels_as_player2 = relationship("SoloDuel", back_populates="player2", foreign_keys="[SoloDuel.player2_id]")

    elo_histories = relationship("EloHistory", back_populates="user", cascade="all, delete-orphan")

    @hybrid_property
    def duels(self):
        return self.solo_duels_as_player1 + self.solo_duels_as_player2