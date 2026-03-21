from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import enum

class Base(DeclarativeBase):
    pass

class PlayerRole(str, enum.Enum):
    WK = "Wicket-Keeper"
    BAT = "Batsman"
    AR = "All-Rounder"
    BOWL = "Bowler"

class MatchStatus(str, enum.Enum):
    UPCOMING = "upcoming"
    LIVE = "live"
    COMPLETED = "completed"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    virtual_credits: Mapped[float] = mapped_column(Float, default=1000.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    fantasy_teams: Mapped[List["FantasyTeam"]] = relationship(back_populates="user")


class Team(Base):
    """Real-world cricket teams (e.g., RCB, SRH)"""
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    abbreviation: Mapped[str] = mapped_column(String(10), unique=True)

    players: Mapped[List["Player"]] = relationship(back_populates="team")


class Player(Base):
    """Real-world cricket players"""
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    role: Mapped[PlayerRole] = mapped_column(Enum(PlayerRole))
    credit_value: Mapped[float] = mapped_column(Float, default=8.5) # Out of 100 budget
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    team: Mapped["Team"] = relationship(back_populates="players")


class Match(Base):
    """Real-world fixtures"""
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    start_time: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[MatchStatus] = mapped_column(Enum(MatchStatus), default=MatchStatus.UPCOMING)
    external_api_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)

    home_team: Mapped["Team"] = relationship(foreign_keys=[home_team_id])
    away_team: Mapped["Team"] = relationship(foreign_keys=[away_team_id])
    fantasy_teams: Mapped[List["FantasyTeam"]] = relationship(back_populates="match")
    player_performances: Mapped[List["PlayerMatchPerformance"]] = relationship(back_populates="match")


class PlayerMatchPerformance(Base):
    """Live scoring data for a player in a specific match"""
    __tablename__ = "player_match_performances"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"))
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    
    # Real-world stats
    runs_scored: Mapped[int] = mapped_column(Integer, default=0)
    balls_faced: Mapped[int] = mapped_column(Integer, default=0)
    fours: Mapped[int] = mapped_column(Integer, default=0)
    sixes: Mapped[int] = mapped_column(Integer, default=0)
    wickets: Mapped[int] = mapped_column(Integer, default=0)
    runs_conceded: Mapped[int] = mapped_column(Integer, default=0)
    overs_bowled: Mapped[float] = mapped_column(Float, default=0.0)
    maidens: Mapped[int] = mapped_column(Integer, default=0)
    catches: Mapped[int] = mapped_column(Integer, default=0)
    stumpings: Mapped[int] = mapped_column(Integer, default=0)
    run_outs: Mapped[int] = mapped_column(Integer, default=0)
    
    # Calculated fantasy points
    total_points: Mapped[float] = mapped_column(Float, default=0.0)
    
    match: Mapped["Match"] = relationship(back_populates="player_performances")
    player: Mapped["Player"] = relationship()

    __table_args__ = (UniqueConstraint("match_id", "player_id", name="uix_match_player"),)


class FantasyTeam(Base):
    """User's fantasy team for a specific match"""
    __tablename__ = "fantasy_teams"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"))
    total_points: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship(back_populates="fantasy_teams")
    match: Mapped["Match"] = relationship(back_populates="fantasy_teams")
    players: Mapped[List["FantasyTeamPlayer"]] = relationship(back_populates="fantasy_team")

    __table_args__ = (UniqueConstraint("user_id", "match_id", name="uix_user_match_fantasy_team"),)


class FantasyTeamPlayer(Base):
    """The individual players chosen in a user's fantasy team"""
    __tablename__ = "fantasy_team_players"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    fantasy_team_id: Mapped[int] = mapped_column(ForeignKey("fantasy_teams.id"))
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    
    is_captain: Mapped[bool] = mapped_column(Boolean, default=False)
    is_vice_captain: Mapped[bool] = mapped_column(Boolean, default=False)
    is_impact_player: Mapped[bool] = mapped_column(Boolean, default=False)

    fantasy_team: Mapped["FantasyTeam"] = relationship(back_populates="players")
    player: Mapped["Player"] = relationship()

    __table_args__ = (UniqueConstraint("fantasy_team_id", "player_id", name="uix_fantasy_team_player"),)
