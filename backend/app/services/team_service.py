"""球队服务层: 提供球队查询/创建/更新/删除与参赛实例及球员历史的组合逻辑。"""
from typing import Dict, List, Any, Optional, Tuple
from app.database import db
from app.models.team import Team
from app.models.team_base import TeamBase
from app.models.team_tournament_participation import TeamTournamentParticipation
from app.models.player import Player
from app.models.player_team_history import PlayerTeamHistory
from app.utils.logger import get_logger
from app.utils.team_utils import TeamUtils

logger = get_logger(__name__)


class TeamService:
    """球队业务逻辑入口。尽量保持方法纯粹: 读取/写入/组装数据，不放多层解释性注释。"""
    
    @staticmethod
    def get_team_by_name_new_api(team_name: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """新架构：基于 TeamBase + Participation 聚合单队全部赛季记录。"""
        try:
            team_base = TeamBase.query.filter_by(name=team_name).first()
            if not team_base:
                return None, '球队不存在'
            
            participations = TeamTournamentParticipation.query.filter_by(team_base_id=team_base.id).all()
            if not participations:
                return None, '未找到球队参赛记录'
            
            historical_stats = team_base.get_historical_stats()
            
            team_info = {
                'teamName': team_name,
                'totalGoals': historical_stats['total_goals'],
                'totalGoalsConceded': historical_stats['total_goals_conceded'],
                'totalGoalDifference': historical_stats['total_goal_difference'],
                'totalRedCards': historical_stats['total_red_cards'],
                'totalYellowCards': historical_stats['total_yellow_cards'],
                'totalPoints': historical_stats['total_points'],
                'totalMatchesPlayed': historical_stats['total_matches_played'],
                'totalWins': historical_stats['total_wins'],
                'totalDraws': historical_stats['total_draws'],
                'totalLosses': historical_stats['total_losses'],
                'bestRank': historical_stats['best_rank'],
                'winRate': historical_stats['win_rate'],
                'records': []
            }
            
            for participation in participations:
                team_record = Team.query.filter_by(
                    tournament_id=participation.tournament_id,
                    team_base_id=team_base.id
                ).first()
                
                record_dict = {
                    'id': participation.id,
                    'teamName': team_name,
                    'tournament_id': participation.tournament_id,
                    'tournament_name': participation.tournament.name if participation.tournament else None,
                    'season_name': participation.tournament.season.name if participation.tournament and participation.tournament.season else None,
                    'competition_name': participation.tournament.competition.name if participation.tournament and participation.tournament.competition else None,
                    'rank': participation.rank,
                    'goals': participation.goals,
                    'goalsConceded': participation.goals_conceded,
                    'goalDifference': participation.goal_difference,
                    'redCards': participation.red_cards,
                    'yellowCards': participation.yellow_cards,
                    'points': participation.points,
                    'matchesPlayed': participation.matches_played,
                    'wins': participation.wins,
                    'draws': participation.draws,
                    'losses': participation.losses
                }
                
                team_players = []
                if team_record:
                    player_histories = PlayerTeamHistory.query.filter_by(
                        team_id=team_record.id, 
                        tournament_id=participation.tournament_id
                    ).all()
                    
                    for history in player_histories:
                        if history.player:
                            team_players.append({
                                'name': history.player.name,
                                'playerId': history.player_id,
                                'studentId': history.player_id,
                                'id': history.player_id,
                                'number': str(history.player_number),
                                'goals': history.tournament_goals,
                                'redCards': history.tournament_red_cards,
                                'yellowCards': history.tournament_yellow_cards
                            })
                
                record_dict['players'] = team_players
                team_info['records'].append(record_dict)
            
            return team_info, None
            
        except Exception as e:
            logger.error(f"Error getting team by name (new API): {e}")
            return None, str(e)
    
    @staticmethod
    def get_team_by_name(team_name: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """旧视图方式：直接从 Team 视图聚合。"""
        try:
            team_records = Team.query.filter_by(name=team_name).all()
            if not team_records:
                return None, '球队不存在'
            
            # 统计总数据
            total_goals = sum(record.tournament_goals for record in team_records)
            total_goals_conceded = sum(record.tournament_goals_conceded for record in team_records)
            total_goal_difference = sum(record.tournament_goal_difference for record in team_records)
            total_red_cards = sum(record.tournament_red_cards for record in team_records)
            total_yellow_cards = sum(record.tournament_yellow_cards for record in team_records)
            total_points = sum(record.tournament_points for record in team_records)
            total_matches_played = sum(record.matches_played for record in team_records)
            total_wins = sum(record.wins for record in team_records)
            total_draws = sum(record.draws for record in team_records)
            total_losses = sum(record.losses for record in team_records)
            
            valid_ranks = [record.tournament_rank for record in team_records if record.tournament_rank and record.tournament_rank > 0]
            best_rank = min(valid_ranks) if valid_ranks else None
            
            # 获取第一个记录的team_base_id（所有记录应该有相同的team_base_id）
            team_base_id = team_records[0].team_base_id if team_records else None
            
            team_info = {
                'teamName': team_name,
                'teamBaseId': team_base_id,  # 添加 team_base_id 字段
                'totalGoals': total_goals,
                'totalGoalsConceded': total_goals_conceded,
                'totalGoalDifference': total_goal_difference,
                'totalRedCards': total_red_cards,
                'totalYellowCards': total_yellow_cards,
                'totalPoints': total_points,
                'totalMatchesPlayed': total_matches_played,
                'totalWins': total_wins,
                'totalDraws': total_draws,
                'totalLosses': total_losses,
                'bestRank': best_rank,
                'records': []
            }
            
            for record in team_records:
                record_dict = record.to_dict()
                record_dict['teamName'] = record_dict['name']
                
                team_players = []
                player_histories = PlayerTeamHistory.query.filter_by(
                    team_id=record.id, 
                    tournament_id=record.tournament_id
                ).all()
                
                for history in player_histories:
                    team_players.append({
                        'name': history.player.name,
                        'playerId': history.player_id,
                        'studentId': history.player_id,
                        'id': history.player_id,
                        'number': str(history.player_number),
                        'goals': history.tournament_goals,
                        'redCards': history.tournament_red_cards,
                        'yellowCards': history.tournament_yellow_cards
                    })
                
                record_dict['players'] = team_players
                record_dict.update({
                    'rank': record.tournament_rank,
                    'goals': record.tournament_goals,
                    'goalsConceded': record.tournament_goals_conceded,
                    'goalDifference': record.tournament_goal_difference,
                    'redCards': record.tournament_red_cards,
                    'yellowCards': record.tournament_yellow_cards,
                    'points': record.tournament_points,
                    'tournamentId': record.tournament_id,
                    'tournamentName': record.tournament.name if record.tournament else None,
                    'seasonId': record.tournament.season_id if record.tournament else None,
                    'seasonName': record.tournament.season.name if record.tournament and record.tournament.season else None
                })
                
                team_info['records'].append(record_dict)
            
            return team_info, None
            
        except Exception as e:
            logger.error(f"Error getting team by name: {e}")
            return None, f'获取失败: {str(e)}'
    
    @staticmethod
    def get_all_teams(group_by_name: bool = False) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
        """获取所有球队信息"""
        try:
            if group_by_name:
                teams = Team.query.all()
                teams_grouped = {}
                
                for team in teams:
                    team_name = team.name
                    if team_name not in teams_grouped:
                        teams_grouped[team_name] = {
                            'teamName': team_name,
                            'totalGoals': 0,
                            'totalGoalsConceded': 0,
                            'totalGoalDifference': 0,
                            'totalRedCards': 0,
                            'totalYellowCards': 0,
                            'totalPoints': 0,
                            'bestRank': None,
                            'tournaments': [],
                            'seasonId': team.tournament.season_id if team.tournament else None, # 添加 seasonId
                            'seasonName': team.tournament.season.name if team.tournament and team.tournament.season else None # 添加 seasonName
                        }
                    
                    teams_grouped[team_name]['totalGoals'] += team.tournament_goals
                    teams_grouped[team_name]['totalGoalsConceded'] += team.tournament_goals_conceded
                    teams_grouped[team_name]['totalGoalDifference'] += team.tournament_goal_difference
                    teams_grouped[team_name]['totalRedCards'] += team.tournament_red_cards
                    teams_grouped[team_name]['totalYellowCards'] += team.tournament_yellow_cards
                    teams_grouped[team_name]['totalPoints'] += team.tournament_points
                    
                    if team.tournament_rank and team.tournament_rank > 0:
                        current_best = teams_grouped[team_name]['bestRank']
                        if current_best is None or team.tournament_rank < current_best:
                            teams_grouped[team_name]['bestRank'] = team.tournament_rank
                    
                    teams_grouped[team_name]['tournaments'].append({
                        'tournamentId': team.tournament_id,
                        'tournamentName': team.tournament.name if team.tournament else None
                    })
                
                return list(teams_grouped.values()), None
            else:
                teams = Team.query.all()
                teams_data = []
                
                for team in teams:
                    team_players = []
                    player_histories = PlayerTeamHistory.query.filter_by(
                        team_id=team.id, 
                        tournament_id=team.tournament_id
                    ).all()
                    
                    for history in player_histories:
                        team_players.append({
                            'name': history.player.name,
                            'playerId': history.player_id,
                            'studentId': history.player_id,
                            'id': history.player_id,
                            'number': str(history.player_number),
                            'goals': history.tournament_goals,
                            'redCards': history.tournament_red_cards,
                            'yellowCards': history.tournament_yellow_cards
                        })
                    
                    standardized_team = {
                        'id': team.id,
                        'teamName': team.name,
                        'name': team.name,
                        'tournamentId': team.tournament_id,
                        'tournamentName': team.tournament.name if team.tournament else None,
                        'seasonId': team.tournament.season_id if team.tournament else None,
                        'seasonName': team.tournament.season.name if team.tournament and team.tournament.season else None,
                        'competitionId': team.tournament.competition_id if team.tournament else None,
                        'competitionName': team.tournament.competition.name if team.tournament and team.tournament.competition else None,
                        'groupId': team.group_id,
                        'rank': team.tournament_rank,
                        'goals': team.tournament_goals,
                        'goalsConceded': team.tournament_goals_conceded,
                        'goalDifference': team.tournament_goal_difference,
                        'redCards': team.tournament_red_cards,
                        'yellowCards': team.tournament_yellow_cards,
                        'points': team.tournament_points,
                        'players': team_players,
                        'createdAt': team.created_at.isoformat() if hasattr(team, 'created_at') and team.created_at else None
                    }
                    
                    teams_data.append(standardized_team)
                
                return teams_data, None
                
        except Exception as e:
            logger.error(f"Error getting all teams: {e}")
            return None, f'获取失败: {str(e)}'
    
    @staticmethod
    def create_team(data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """创建参赛实例: 解析/创建赛事 -> 基础球队复用 -> participation -> 球员历史。"""
        try:
            tournament_id, terr = TeamService._resolve_or_create_tournament(data)
            if terr:
                return None, terr

            team_name = data.get('teamName')
            if not team_name:
                return None, '缺少 teamName'

            # 1. 基础球队：存在则复用，否则创建
            team_base = TeamBase.query.filter_by(name=team_name).first()
            if not team_base:
                team_base = TeamBase(name=team_name)
                db.session.add(team_base)
                db.session.flush()

            # 2. 检查是否已有该赛事 active participation
            existing_participation = TeamTournamentParticipation.query.filter_by(team_base_id=team_base.id, tournament_id=tournament_id).first()
            
            is_new_team = False
            if existing_participation:
                # 如果已存在，复用该参赛记录
                participation = existing_participation
                # 如果有传入 group_id，更新它
                if data.get('groupId'):
                    participation.group_id = data.get('groupId')
            else:
                is_new_team = True
                # 如果不存在，创建新的参赛记录
                participation = TeamTournamentParticipation(
                    team_base_id=team_base.id,
                    tournament_id=tournament_id,
                    group_id=data.get('groupId')
                )
                db.session.add(participation)
                db.session.flush()

            # 3. 处理球员
            players_data = data.get('players', []) or []
            for p in players_data:
                pid = p.get('studentId') or p.get('playerId')
                pname = p.get('name')
                if not pid or not pname:
                    continue
                
                # 确保球员存在
                player = Player.query.get(pid)
                if not player:
                    player = Player(id=pid, name=pname)
                    db.session.add(player)
                else:
                    player.name = pname
                
                number = int(p.get('number') or 0) if str(p.get('number')).isdigit() else 0
                
                # 检查该球员是否已在该参赛队伍中
                existing_history = PlayerTeamHistory.query.filter_by(
                    player_id=pid,
                    team_id=participation.id,
                    tournament_id=tournament_id
                ).first()
                
                if existing_history:
                    # 如果已存在，更新号码
                    existing_history.player_number = number
                else:
                    # 如果不存在，添加新记录
                    db.session.add(PlayerTeamHistory(
                        player_id=pid, 
                        player_number=number, 
                        team_id=participation.id, 
                        tournament_id=tournament_id
                    ))

            db.session.commit()
            result = TeamService._build_participation_response(participation)
            result['is_new'] = is_new_team
            return result, None
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error creating team (dynamic tournament): {e}')
            return None, f'创建失败: {e}'
    
    @staticmethod
    def update_team(team_id: int, data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """更新参赛实例 (team_id 即 participation.id)。"""
        try:
            participation = TeamTournamentParticipation.query.get(team_id)
            if not participation:
                return None, '参赛记录不存在'

            # 更新基础名称（team_base）
            if data.get('teamName'):
                # 检查重名
                same_name = TeamBase.query.filter(TeamBase.name == data['teamName'], TeamBase.id != participation.team_base_id).first()
                if same_name:
                    return None, '存在同名基础球队'
                participation.team_base.name = data['teamName']

            # 更新赛事类型（不支持直接跨赛事迁移，需删除重建）
            if data.get('matchType'):
                match_type_to_tournament = {
                    'champions-cup': 1,
                    'womens-cup': 2,
                    'eight-a-side': 3
                }
                new_tid = match_type_to_tournament.get(data['matchType'], participation.tournament_id)
                if new_tid != participation.tournament_id:
                    return None, '暂不支持直接修改赛事类型，请删除后重新创建'

            if 'groupId' in data:
                participation.group_id = data.get('groupId')

            # 重建球员（简单方案：全删再插）
            if 'players' in data:
                PlayerTeamHistory.query.filter_by(team_id=participation.id, tournament_id=participation.tournament_id).delete()
                players_data = data.get('players') or []
                for p in players_data:
                    pid = p.get('studentId') or p.get('playerId')
                    pname = p.get('name')
                    if not pid or not pname:
                        continue
                    player = Player.query.get(pid)
                    if not player:
                        player = Player(id=pid, name=pname)
                        db.session.add(player)
                    else:
                        player.name = pname
                    number = int(p.get('number') or 0) if str(p.get('number')).isdigit() else 0
                    history = PlayerTeamHistory(
                        player_id=pid,
                        player_number=number,
                        team_id=participation.id,
                        tournament_id=participation.tournament_id
                    )
                    db.session.add(history)

            db.session.commit()
            return TeamService._build_participation_response(participation), None
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error updating team (new path): {e}')
            return None, f'更新失败: {e}'

    @staticmethod
    def delete_team(team_id: int) -> Tuple[bool, Optional[str]]:
        """删除参赛实例及其球员历史（不删 TeamBase）。"""
        try:
            participation = TeamTournamentParticipation.query.get(team_id)
            if not participation:
                return False, '参赛记录不存在'

            # 删除相关球员历史
            PlayerTeamHistory.query.filter_by(team_id=participation.id, tournament_id=participation.tournament_id).delete()
            db.session.delete(participation)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error deleting team (new path): {e}')
            return False, f'删除失败: {e}'
    
    @staticmethod
    def _build_team_response(team: Team) -> Dict[str, Any]:
        """旧视图兼容响应构造。"""
        participation = TeamTournamentParticipation.query.get(team.id)
        if not participation:
            # 退化：使用视图字段简单返回
            return {
                'id': team.id,
                'teamName': team.name,
                'tournamentId': team.tournament_id,
                'tournamentName': team.tournament.name if team.tournament else None,
                'groupId': team.group_id,
                'rank': team.tournament_rank,
                'goals': team.tournament_goals,
                'goalsConceded': team.tournament_goals_conceded,
                'goalDifference': team.tournament_goal_difference,
                'redCards': team.tournament_red_cards,
                'yellowCards': team.tournament_yellow_cards,
                'points': team.tournament_points,
                'players': [],
                'matchesPlayed': team.matches_played,
                'wins': team.wins,
                'draws': team.draws,
                'losses': team.losses
            }
        return TeamService._build_participation_response(participation)
    
    @staticmethod
    def _build_participation_response(participation: TeamTournamentParticipation) -> Dict[str, Any]:
        team_base = participation.team_base
        tournament = participation.tournament
        histories = PlayerTeamHistory.query.filter_by(team_id=participation.id, tournament_id=participation.tournament_id).all()
        players = []
        for h in histories:
            players.append({
                'name': h.player.name if h.player else None,
                'playerId': h.player_id,
                'studentId': h.player_id,
                'id': h.player_id,
                'number': str(h.player_number),
                'goals': h.tournament_goals,
                'redCards': h.tournament_red_cards,
                'yellowCards': h.tournament_yellow_cards
            })
        return {
            'id': participation.id,
            'teamName': team_base.name if team_base else None,
            'tournamentId': participation.tournament_id,
            'tournamentName': tournament.name if tournament else None,
            'competitionId': tournament.competition_id if tournament else None,
            'groupId': participation.group_id,
            'rank': participation.tournament_rank,
            'goals': participation.tournament_goals,
            'goalsConceded': participation.tournament_goals_conceded,
            'goalDifference': participation.tournament_goal_difference,
            'redCards': participation.tournament_red_cards,
            'yellowCards': participation.tournament_yellow_cards,
            'points': participation.tournament_points,
            'players': players,
            'matchesPlayed': participation.matches_played,
            'wins': participation.wins,
            'draws': participation.draws,
            'losses': participation.losses
        }
    
    @staticmethod
    def _resolve_or_create_tournament(data: Dict[str, Any]) -> Tuple[Optional[int], Optional[str]]:
        """解析/创建赛事: 优先 tournamentId > (competitionName+seasonName) > matchType 映射。"""
        from app.models.tournament import Tournament
        from app.models.competition import Competition
        from app.models.season import Season
        from datetime import datetime, timedelta

        if 'tournamentId' in data and data['tournamentId']:
            t = Tournament.query.get(data['tournamentId'])
            return (t.id, None) if t else (None, '指定 tournamentId 不存在')

        # 新增: 支持 competitionId (自动查找最新赛季)
        if 'competitionId' in data and data['competitionId']:
            comp_id = data['competitionId']
            # 查找该赛事下最新的 tournament (按 season_id 倒序? 或 season.start_time 倒序)
            # 这里简单按 season_id 倒序
            latest_t = Tournament.query.filter_by(competition_id=comp_id)\
                .join(Season).order_by(Season.start_time.desc()).first()
            
            if latest_t:
                return latest_t.id, None
            else:
                return None, '该赛事下暂无赛季记录，请先创建赛季赛事'

        comp_name = data.get('competitionName')
        season_name = data.get('seasonName')
        if comp_name and season_name:
            comp = Competition.query.filter_by(name=comp_name).first()
            if not comp:
                comp = Competition(name=comp_name)
                db.session.add(comp)
                db.session.flush()
            season = Season.query.filter_by(name=season_name).first()
            if not season:
                start = datetime.utcnow()
                end = start + timedelta(days=90)
                season = Season(name=season_name, start_time=start, end_time=end)
                db.session.add(season)
                db.session.flush()
            existing = Tournament.query.filter_by(competition_id=comp.competition_id, season_id=season.season_id).first()
            if existing:
                return existing.id, None
            new_t = Tournament(competition_id=comp.competition_id, season_id=season.season_id)
            db.session.add(new_t)
            db.session.flush()
            return new_t.id, None

        # fallback: matchType (支持中文/别名)
        raw_type = data.get('matchType', 'champions-cup')
        canonical, mt_err = TeamUtils.normalize_match_type(raw_type)
        if mt_err:
            return None, mt_err + '；或提供 competitionName+seasonName'

        match_type_to_tournament = {
            'champions-cup': 1,
            'womens-cup': 2,
            'eight-a-side': 3
        }
        tid = match_type_to_tournament.get(canonical)
        if tid is None:
            valid_cn = ['冠军杯/校园杯', '巾帼杯/女子杯/女足杯', '八人制/八人赛/8人制']
            valid_en = list(match_type_to_tournament.keys())
            return None, f"无效的比赛类型({raw_type})。有效类型(英文): {', '.join(valid_en)} | (中文): {', '.join(valid_cn)}；或提供 competitionName+seasonName"
        from app.models.tournament import Tournament as T
        if not T.query.get(tid):
            return None, f'目标赛事不存在 (ID={tid})，请提供 competitionName+seasonName 创建'
        return tid, None
