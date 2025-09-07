"""
比赛模块服务层 - 处理比赛相关的核心业务逻辑
"""

from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import or_
from app.database import db
from app.models.match import Match
from app.models.team import Team
from app.models.tournament import Tournament
from app.models.event import Event
from app.models.player import Player
from app.models.player_team_history import PlayerTeamHistory
from app.utils.match_utils import MatchUtils
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MatchService:
    """比赛服务类"""

    def __init__(self):
        self.utils = MatchUtils()

    def create_match(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建比赛"""
        try:
            # 获取赛事ID和球队
            tournament_id = MatchUtils.get_tournament_id_by_type(
                data.get('matchType', 'champions-cup')
            )
            
            team1 = Team.query.filter_by(
                name=data['team1'], 
                tournament_id=tournament_id
            ).first()
            team2 = Team.query.filter_by(
                name=data['team2'], 
                tournament_id=tournament_id
            ).first()
            
            if not team1 or not team2:
                raise ValueError('球队不存在')
            
            # 生成比赛ID和解析时间
            existing_matches = Match.query.filter_by(tournament_id=tournament_id).count()
            match_id = MatchUtils.generate_match_id(tournament_id, existing_matches)
            
            match_time = MatchUtils.parse_date_from_frontend(data['date'])
            if match_time is None:
                from datetime import datetime
                match_time = datetime.now()
            
            # 创建比赛记录
            new_match = Match(
                id=match_id,
                match_name=data['matchName'],
                match_time=match_time,
                location=data['location'],
                home_team_id=team1.id,
                away_team_id=team2.id,
                tournament_id=tournament_id,
                status='P'
            )
            
            db.session.add(new_match)
            db.session.commit()
            
            # 构建返回数据
            tournament = Tournament.query.get(tournament_id)
            match_dict = self._build_match_response(new_match, tournament)
            match_dict['team1'] = data['team1']
            match_dict['team2'] = data['team2']
            
            MatchUtils.log_match_operation("创建比赛", match_id, f"赛事: {data['matchName']}")
            
            return {
                'status': 'success',
                'message': '比赛创建成功',
                'data': match_dict
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建比赛失败: {str(e)}")
            raise

    def complete_match(self, match_id: str) -> Dict[str, Any]:
        """标记比赛为已完赛"""
        match = Match.query.get(match_id)
        if not match:
            raise ValueError('比赛不存在')
        
        if match.status == 'F':
            raise ValueError('比赛已经完赛')
        
        match.status = 'F'
        db.session.commit()
        
        MatchUtils.log_match_operation("完赛比赛", match_id)
        
        return {
            'status': 'success',
            'message': '比赛已标记为完赛',
            'data': {
                'id': match.id,
                'status': '已完赛'
            }
        }

    def get_all_matches(self) -> Dict[str, Any]:
        """获取所有比赛"""
        matches = Match.query.all()
        matches_data = []
        
        for match in matches:
            tournament = Tournament.query.get(match.tournament_id)
            match_dict = MatchUtils.build_match_dict_with_type(match, tournament)
            matches_data.append(match_dict)
        
        return {
            'status': 'success',
            'data': matches_data
        }

    def update_match(self, match_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """更新比赛信息"""
        match = Match.query.get(match_id)
        if not match:
            raise ValueError('比赛不存在')
        
        # 更新比赛类型
        if data.get('matchType'):
            new_tournament_id = MatchUtils.get_tournament_id_by_type(data['matchType'])
            match.tournament_id = new_tournament_id
        
        # 更新基本信息
        if data.get('matchName'):
            match.match_name = data['matchName']
        
        if data.get('date'):
            match_time = MatchUtils.parse_date_from_frontend(data['date'])
            if match_time:
                match.match_time = match_time
        
        if data.get('location'):
            match.location = data['location']
        
        # 更新比分
        if 'home_score' in data:
            match.home_score = MatchUtils.safe_int_conversion(data['home_score'])
        
        if 'away_score' in data:
            match.away_score = MatchUtils.safe_int_conversion(data['away_score'])
        
        # 更新球队
        if data.get('team1'):
            team1 = Team.query.filter_by(
                name=data['team1'], 
                tournament_id=match.tournament_id
            ).first()
            if team1:
                match.home_team_id = team1.id
        
        if data.get('team2'):
            team2 = Team.query.filter_by(
                name=data['team2'], 
                tournament_id=match.tournament_id
            ).first()
            if team2:
                match.away_team_id = team2.id
        
        db.session.commit()
        
        # 返回更新后的数据
        tournament = Tournament.query.get(match.tournament_id)
        match_dict = MatchUtils.build_match_dict_with_type(match, tournament)
        
        MatchUtils.log_match_operation("更新比赛", match_id, f"更新字段: {list(data.keys())}")
        
        return {
            'status': 'success',
            'message': '更新成功',
            'data': match_dict
        }

    def delete_match(self, match_id: str) -> Dict[str, Any]:
        """删除比赛"""
        match = Match.query.get(match_id)
        if not match:
            raise ValueError('比赛不存在')
        
        # 删除关联的事件
        Event.query.filter_by(match_id=match_id).delete()
        
        # 删除比赛
        db.session.delete(match)
        db.session.commit()
        
        MatchUtils.log_match_operation("删除比赛", match_id)
        
        return {
            'status': 'success',
            'message': '删除成功'
        }

    def get_match_records(self, match_type: str = '', status_filter: str = '', 
                         keyword: str = '', page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """获取比赛记录，支持筛选和分页"""
        query = Match.query

        # 筛选条件
        if match_type:
            tournament_id = MatchUtils.get_tournament_id_by_frontend_type(match_type)
            if tournament_id:
                query = query.filter(Match.tournament_id == tournament_id)

        if status_filter:
            db_status = MatchUtils.get_status_code(status_filter)
            if db_status:
                query = query.filter(Match.status == db_status)

        if keyword:
            query = query.filter(
                or_(
                    Match.match_name.ilike(f'%{keyword}%'),
                    Match.location.ilike(f'%{keyword}%'),
                    Match.home_team.has(Team.name.ilike(f'%{keyword}%')),
                    Match.away_team.has(Team.name.ilike(f'%{keyword}%'))
                )
            )

        total = query.count()
        matches = query.order_by(Match.match_time.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size).all()

        # 构建返回数据
        records = []
        for match in matches:
            match_dict = MatchUtils.build_match_dict_basic(match)
            match_dict['id'] = match.id
            match_dict['name'] = match.match_name
            match_dict['location'] = match.location
            match_dict['home_own_goals'] = 0
            match_dict['away_own_goals'] = 0
            
            tournament = Tournament.query.get(match.tournament_id)
            match_dict['matchType'] = MatchUtils.determine_match_type(tournament)
            
            records.append(match_dict)

        return {
            'status': 'success',
            'data': {
                'records': records,
                'total': total,
                'page': page,
                'pageSize': page_size
            }
        }

    def get_match_detail(self, match_id: str) -> Dict[str, Any]:
        """获取比赛详细信息"""
        match = Match.query.get(match_id.strip())
        if not match:
            raise ValueError(f'未找到ID为{match_id}的比赛')
        
        # 获取比赛事件
        events = Event.query.filter_by(match_id=match_id).order_by(Event.event_time.asc()).all()
        logger.info(f"找到 {len(events)} 个事件记录")
        
        # 构建返回数据
        events_data = self._build_events_data(events, match.tournament_id)
        statistics = self._calculate_match_statistics(events, match.home_team_id, match.away_team_id)
        players_data = self._get_players_data(events, match)
        match_data = self._build_detailed_match_data(match, statistics, players_data, events_data)
        
        return {
            'status': 'success',
            'data': match_data
        }

    def _build_match_response(self, match, tournament) -> Dict[str, Any]:
        """构建比赛响应数据"""
        match_dict = match.to_dict()
        match_dict['matchName'] = match_dict['match_name']
        match_dict['date'] = MatchUtils.format_match_time(match.match_time)
        match_dict['matchType'] = MatchUtils.determine_match_type(tournament)
        return match_dict

    def _build_events_data(self, events: List, tournament_id: int) -> List[Dict[str, Any]]:
        """构建事件数据用于前端展示"""
        events_data = []
        for event in events:
            player_name = '未知球员'
            team_name = '未知球队'
            
            if event.player_id:
                player = Player.query.get(event.player_id)
                if player:
                    player_name = player.name or '未知球员'
                    # 优先从球员队伍历史记录获取队伍名称
                    team_history = PlayerTeamHistory.query.filter_by(
                        player_id=event.player_id,
                        tournament_id=tournament_id
                    ).first()
                    if team_history and team_history.team:
                        team_name = team_history.team.name
                    elif player.team:
                        team_name = player.team.name
            
            # 如果事件直接关联了队伍，使用事件的队伍信息
            if event.team_id:
                team = Team.query.get(event.team_id)
                if team:
                    team_name = team.name
            
            event_data = {
                'id': event.id,
                'event_type': event.event_type,
                'event_time': event.event_time or 0,
                'player_id': event.player_id,
                'player_name': player_name,
                'team_id': event.team_id,
                'team_name': team_name,
                'event_type_text': event.event_type
            }
            events_data.append(event_data)
        
        return events_data

    def _calculate_match_statistics(self, events: List, home_team_id: int, away_team_id: int) -> Dict[str, Any]:
        """计算比赛统计数据"""
        # 基础统计
        total_goals = sum(1 for event in events if event.event_type == '进球')
        total_own_goals = sum(1 for event in events if event.event_type == '乌龙球')
        total_yellow_cards = sum(1 for event in events if event.event_type == '黄牌')
        total_red_cards = sum(1 for event in events if event.event_type == '红牌')
        
        # 使用工具类计算队伍统计
        home_stats = MatchUtils.calculate_team_statistics(events, home_team_id)
        away_stats = MatchUtils.calculate_team_statistics(events, away_team_id)
        
        # 计算实际得分
        home_score_from_events, away_score_from_events = MatchUtils.calculate_score_from_events(
            events, home_team_id, away_team_id
        )
        
        return {
            'total_goals': total_goals,
            'total_own_goals': total_own_goals,
            'total_yellow_cards': total_yellow_cards,
            'total_red_cards': total_red_cards,
            'home_goals': home_stats['goals'],
            'away_goals': away_stats['goals'],
            'home_own_goals': home_stats['own_goals'],
            'away_own_goals': away_stats['own_goals'],
            'home_yellow_cards': home_stats['yellow_cards'],
            'away_yellow_cards': away_stats['yellow_cards'],
            'home_red_cards': home_stats['red_cards'],
            'away_red_cards': away_stats['red_cards'],
            'home_score_from_events': home_score_from_events,
            'away_score_from_events': away_score_from_events
        }

    def _get_players_data(self, events: List, match) -> List[Dict[str, Any]]:
        """获取参赛球员信息"""
        players_data = []
        all_players = set()
        
        # 从事件中获取参与的球员
        for event in events:
            if event.player_id:
                all_players.add(event.player_id)
        
        # 获取两支队伍的所有球员
        total_team_players = 0
        if match.home_team_id and match.away_team_id:
            home_team_histories = PlayerTeamHistory.query.filter_by(
                team_id=match.home_team_id,
                tournament_id=match.tournament_id
            ).all()
            
            away_team_histories = PlayerTeamHistory.query.filter_by(
                team_id=match.away_team_id,
                tournament_id=match.tournament_id
            ).all()
            
            total_team_players = len(home_team_histories) + len(away_team_histories)
            
            # 将所有队伍球员加入到all_players集合中
            for history in home_team_histories + away_team_histories:
                if history.player_id:
                    all_players.add(history.player_id)
        
        logger.info(f"找到 {len(all_players)} 个参赛球员")
        
        # 为每个球员统计数据
        for player_id in all_players:
            try:
                player = Player.query.get(player_id)
                if not player:
                    continue
                
                # 获取球员在此赛事中的队伍归属
                team_history = PlayerTeamHistory.query.filter_by(
                    player_id=player_id,
                    tournament_id=match.tournament_id
                ).first()
                
                # 统计该球员在本场比赛的各类事件
                player_events = [e for e in events if e.player_id == player_id]
                player_goals = sum(1 for e in player_events if e.event_type == '进球')
                player_own_goals = sum(1 for e in player_events if e.event_type == '乌龙球')
                player_yellow_cards = sum(1 for e in player_events if e.event_type == '黄牌')
                player_red_cards = sum(1 for e in player_events if e.event_type == '红牌')
                
                # 获取球员号码和队伍名称
                player_number = 0
                team_name = '未知球队'
                
                if team_history:
                    player_number = team_history.player_number or 0
                    team_name = team_history.team.name if team_history.team else '未知球队'
                elif player.team:
                    team_name = player.team.name
                    player_number = player.number or 0
                
                players_data.append({
                    'player_id': player.id,
                    'player_name': player.name or '未知球员',
                    'team_name': team_name,
                    'player_number': player_number,
                    'goals': player_goals,
                    'own_goals': player_own_goals,
                    'yellow_cards': player_yellow_cards,
                    'red_cards': player_red_cards
                })
                
            except Exception as player_error:
                logger.error(f"处理球员{player_id}数据时出错: {player_error}")
                continue
        
        # 设置总球员数
        setattr(self, '_total_players', total_team_players)
        return players_data

    def _build_detailed_match_data(self, match, statistics: Dict[str, Any], 
                                 players_data: List[Dict[str, Any]], 
                                 events_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """构建详细的比赛数据"""
        total_players = getattr(self, '_total_players', 0)
        
        match_data = {
            'id': match.id,
            'home_team_name': match.home_team.name if match.home_team else '主队',
            'away_team_name': match.away_team.name if match.away_team else '客队',
            'home_score': match.home_score if match.home_score is not None else statistics['home_score_from_events'],
            'away_score': match.away_score if match.away_score is not None else statistics['away_score_from_events'],
            'match_date': MatchUtils.format_match_date_iso(match.match_time),
            'tournament_name': match.tournament.name if match.tournament else '友谊赛',
            'season_name': f"{match.match_time.year}赛季" if match.match_time else '2024赛季',
            'status': match.status or 'P',
            'total_players': total_players,
            'players': players_data,
            'events': events_data
        }
        
        # 添加统计数据
        match_data.update(statistics)
        
        return match_data
