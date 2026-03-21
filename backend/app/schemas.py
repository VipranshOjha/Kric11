from pydantic import BaseModel, model_validator
from typing import List
from app.models import PlayerRole

class PlayerSelection(BaseModel):
    player_id: int
    role: PlayerRole
    credit_value: float
    is_captain: bool = False
    is_vice_captain: bool = False
    is_impact_player: bool = False

class FantasyTeamCreate(BaseModel):
    match_id: int
    players: List[PlayerSelection]

    @model_validator(mode='after')
    def validate_team_constraints(self):
        # 1. Check player counts (12 total: 11 main + 1 impact)
        if len(self.players) != 12:
            raise ValueError("Exactly 12 players (11 main + 1 impact sub) must be selected.")
        
        main_players = [p for p in self.players if not p.is_impact_player]
        impact_players = [p for p in self.players if p.is_impact_player]

        if len(main_players) != 11:
            raise ValueError("Exactly 11 main players must be selected.")
        
        if len(impact_players) != 1:
            raise ValueError("Exactly 1 impact player must be selected.")

        # 2. Check credits for main players
        # Constraints: 100 credits maximum for the starting XI
        total_credits = sum(p.credit_value for p in main_players)
        if total_credits > 100.0:
            raise ValueError(f"Total budget exceeded! Used: {total_credits}, Max: 100.0")

        # 3. Check role constraints in main 11 players
        role_counts = {role: 0 for role in PlayerRole}
        for p in main_players:
            role_counts[p.role] += 1
        
        if not (1 <= role_counts[PlayerRole.WK] <= 4):
            raise ValueError("Must select between 1 and 4 Wicket-Keepers in the starting XI.")
        if not (3 <= role_counts[PlayerRole.BAT] <= 6):
            raise ValueError("Must select between 3 and 6 Batsmen in the starting XI.")
        if not (1 <= role_counts[PlayerRole.AR] <= 4):
            raise ValueError("Must select between 1 and 4 All-Rounders in the starting XI.")
        if not (3 <= role_counts[PlayerRole.BOWL] <= 6):
            raise ValueError("Must select between 3 and 6 Bowlers in the starting XI.")

        # 4. Check Captain & Vice Captain assignments
        captains = [p for p in main_players if p.is_captain]
        vice_captains = [p for p in main_players if p.is_vice_captain]

        if len(captains) != 1:
            raise ValueError("Exactly 1 Captain must be selected from the main 11 players.")
        if len(vice_captains) != 1:
            raise ValueError("Exactly 1 Vice-Captain must be selected from the main 11 players.")
        
        # 5. Check for duplicate players across the entire 12-man roster
        player_ids = set()
        for p in self.players:
            if p.player_id in player_ids:
                raise ValueError(f"Duplicate player selected: ID {p.player_id}")
            player_ids.add(p.player_id)
            
        return self
