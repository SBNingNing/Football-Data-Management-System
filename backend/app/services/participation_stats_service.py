from typing import List, Dict, Any
from app.models.team_tournament_participation import TeamTournamentParticipation
from app.utils.stats_utils import StatsUtils


class ParticipationStatsService:
    """Participation-focused statistics service.

    Scope:
    - Per participation (team within one tournament) metrics.
    - Ranking data within a single tournament (participation centric).
    - Cross-tournament comparison for a single team_base.
    - (Optional) aggregate totals for a team across tournaments.

    Out of scope: match-level global stats (handled by StatsService).
    """

    # ---- Per participation metrics (renamed from calculate_team_participation_stats in old service) ----
    @staticmethod
    def calculate_participation_metrics(participation: TeamTournamentParticipation) -> Dict[str, Any]:
        participation_data = {
            'matches_played': participation.matches_played or 0,
            'wins': participation.wins or 0,
            'draws': participation.draws or 0,
            'losses': participation.losses or 0,
            'goals_for': participation.tournament_goals or 0,
            'goals_against': participation.tournament_goals_conceded or 0,
            'points': participation.tournament_points or 0,
            'rank': participation.tournament_rank,
            'red_cards': participation.tournament_red_cards or 0,
            'yellow_cards': participation.tournament_yellow_cards or 0
        }
        return StatsUtils.calculate_team_participation_metrics(participation_data)

    # ---- Tournament ranking (renamed from get_team_tournament_ranking) ----
    @staticmethod
    def list_tournament_participations(tournament_id: int) -> List[Dict[str, Any]]:
        participations = TeamTournamentParticipation.query.filter_by(
            tournament_id=tournament_id,
            status='active'
        ).order_by(
            TeamTournamentParticipation.tournament_rank.asc()
        ).all()

        rankings: List[Dict[str, Any]] = []
        for p in participations:
            stats = ParticipationStatsService.calculate_participation_metrics(p)
            rankings.append({
                'team_base_id': p.team_base_id,
                'team_name': p.team_base.name if p.team_base else None,
                'rank': p.tournament_rank,
                'stats': stats
            })
        return rankings

    # ---- Cross tournament comparison (renamed from compare_team_performances) ----
    @staticmethod
    def compare_team_performances(team_base_id: int, tournament_ids: List[int]) -> Dict[str, Any]:
        participations = TeamTournamentParticipation.query.filter(
            TeamTournamentParticipation.team_base_id == team_base_id,
            TeamTournamentParticipation.tournament_id.in_(tournament_ids),
            TeamTournamentParticipation.status == 'active'
        ).all()

        comparisons: List[Dict[str, Any]] = []
        for p in participations:
            stats = ParticipationStatsService.calculate_participation_metrics(p)
            tournament_name = p.tournament.name if p.tournament else 'Unknown'
            comparisons.append({
                'tournament_id': p.tournament_id,
                'tournament_name': tournament_name,
                'stats': stats
            })

        return {
            'team_base_id': team_base_id,
            'comparisons': comparisons,
            'summary': StatsUtils.calculate_overall_tournament_summary([c['stats'] for c in comparisons])
        }

    # ---- Aggregate totals across tournaments for one team (new helper kept) ----
    @staticmethod
    def aggregate_team_totals(team_base_id: int) -> Dict[str, Any]:
        participations = TeamTournamentParticipation.query.filter(
            TeamTournamentParticipation.team_base_id == team_base_id,
            TeamTournamentParticipation.status == 'active'
        ).all()
        total_matches = sum(p.matches_played or 0 for p in participations)
        total_wins = sum(p.wins or 0 for p in participations)
        total_draws = sum(p.draws or 0 for p in participations)
        total_losses = sum(p.losses or 0 for p in participations)
        goals_for = sum(p.tournament_goals or 0 for p in participations)
        goals_against = sum(p.tournament_goals_conceded or 0 for p in participations)
        return {
            'team_base_id': team_base_id,
            'total_matches': total_matches,
            'total_wins': total_wins,
            'total_draws': total_draws,
            'total_losses': total_losses,
            'goals_for': goals_for,
            'goals_against': goals_against,
        }
