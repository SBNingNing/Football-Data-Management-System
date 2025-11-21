"""统计门面层：统一聚合底层多统计服务输出，供路由调用。

避免路由直接依赖多个 service，集中兼容未来合并/缓存/降级策略。
"""
from typing import Any, Dict, List
from app.services.stats_service import StatsService
from app.services.participation_stats_service import ParticipationStatsService
from app.utils.logger import get_logger

logger = get_logger(__name__)

class StatsFacade:
    @staticmethod
    def overview() -> Dict[str, Any]:
        """系统整体比赛概览统计"""
        return StatsService.get_match_statistics()

    @staticmethod
    def all_rankings(season_id: int = None) -> Dict[str, Any]:
        """所有赛事的多维排行榜（射手 / 牌数 / 积分）"""
        return StatsService.get_all_rankings(season_id)

    @staticmethod
    def tournament_points_ranking(tournament_id: int) -> List[Dict[str, Any]]:
        """赛事积分榜（老逻辑保留）"""
        return StatsService.calculate_team_points(tournament_id)

    @staticmethod
    def tournament_detail_stats(tournament_id: int) -> Dict[str, Any]:
        """赛事综合统计（比赛/球队/场均）"""
        return StatsService.get_tournament_statistics(tournament_id)

    @staticmethod
    def tournament_team_rankings(tournament_id: int) -> List[Dict[str, Any]]:
        """基于 TeamTournamentParticipation 的排名（新结构）"""
        try:
            return ParticipationStatsService.list_tournament_participations(tournament_id)
        except Exception as e:
            logger.error(f"获取赛事 {tournament_id} participation 排名失败: {e}")
            return []

    @staticmethod
    def tournament_comparison(team_base_id: int, tournament_ids: List[int]) -> Dict[str, Any]:
        return ParticipationStatsService.compare_team_performances(team_base_id, tournament_ids)
