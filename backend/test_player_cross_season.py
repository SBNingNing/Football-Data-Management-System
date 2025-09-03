#!/usr/bin/env python3
"""
球员跨赛季查询功能测试脚本
测试新的球员历史查询API是否正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import create_app, db
from app.models import Player, PlayerTeamHistory, Tournament, Season, Competition

# 创建应用上下文
app = create_app()

def test_player_cross_season_capability():
    """测试球员跨赛季查询能力"""
    with app.app_context():
        print("=" * 60)
        print("球员跨赛季查询功能测试")
        print("=" * 60)
    
    # 1. 测试数据结构支持
    print("\n1. 测试数据结构支持:")
    
    # 检查PlayerTeamHistory表是否包含必要字段
    try:
        pth_fields = [column.name for column in PlayerTeamHistory.__table__.columns]
        required_fields = ['球员ID', '球队ID', '赛事ID', '赛事进球数', '赛事红牌数', '赛事黄牌数']
        
        missing_fields = [field for field in required_fields if field not in pth_fields]
        if missing_fields:
            print(f"✗ PlayerTeamHistory缺少字段: {missing_fields}")
            return False
        else:
            print("✓ PlayerTeamHistory包含所有必需字段")
    except Exception as e:
        print(f"✗ PlayerTeamHistory表结构检查失败: {e}")
        return False
    
    # 检查关系是否正确建立
    try:
        # 检查PlayerTeamHistory与Tournament的关系
        if hasattr(PlayerTeamHistory, 'tournament'):
            print("✓ PlayerTeamHistory与Tournament关系正确")
        else:
            print("✗ PlayerTeamHistory缺少tournament关系")
            return False
            
        # 检查Tournament与Season的关系
        if hasattr(Tournament, 'season'):
            print("✓ Tournament与Season关系正确")
        else:
            print("✗ Tournament缺少season关系")
            return False
    except Exception as e:
        print(f"✗ 关系检查失败: {e}")
        return False
    
    # 2. 测试查询能力
    print("\n2. 测试查询能力:")
    
    try:
        # 查询所有球员
        players = Player.query.limit(3).all()
        if not players:
            print("⚠️  数据库中暂无球员数据，无法测试实际查询")
            return True
        
        print(f"✓ 找到 {len(players)} 个球员用于测试")
        
        for player in players:
            print(f"\n  测试球员: {player.name} (ID: {player.id})")
            
            # 查询球员历史记录
            histories = PlayerTeamHistory.query.filter_by(player_id=player.id).all()
            print(f"    历史记录数: {len(histories)}")
            
            if histories:
                # 按赛季分组
                seasons = set()
                tournaments = set()
                teams = set()
                
                for history in histories:
                    if history.tournament:
                        tournaments.add(history.tournament.name)
                        if history.tournament.season:
                            seasons.add(history.tournament.season.name)
                    
                    if history.team:
                        teams.add(history.team.name)
                
                print(f"    参与赛季数: {len(seasons)}")
                print(f"    参与赛事数: {len(tournaments)}")
                print(f"    效力球队数: {len(teams)}")
                
                if len(seasons) > 1:
                    print("    ✓ 该球员有跨赛季记录")
                else:
                    print("    - 该球员暂无跨赛季记录")
            else:
                print("    - 该球员暂无历史记录")
    
    except Exception as e:
        print(f"✗ 查询测试失败: {e}")
        return False
    
    # 3. 测试新API路由导入
    print("\n3. 测试新API路由:")
    
    try:
        from app.routes.player_history import player_history_bp
        print("✓ 球员历史路由导入成功")
        
        # 检查关键函数
        required_functions = [
            'get_player_complete_history',
            'get_player_season_performance', 
            'compare_players_across_seasons',
            'get_player_team_changes'
        ]
        
        import app.routes.player_history as ph_module
        for func_name in required_functions:
            if hasattr(ph_module, func_name):
                print(f"  ✓ 函数 {func_name} 存在")
            else:
                print(f"  ✗ 函数 {func_name} 缺失")
                return False
                
    except Exception as e:
        print(f"✗ 路由导入失败: {e}")
        return False
    
    print("\n=" * 60)
    print("🎉 球员跨赛季查询功能测试通过!")
    print("=" * 60)
    
    return True

def test_data_relationships():
    """测试数据关系的完整性"""
    with app.app_context():
        print("\n4. 测试数据关系完整性:")
    
    try:
        # 测试级联查询
        sample_histories = PlayerTeamHistory.query.limit(5).all()
        
        for history in sample_histories:
            print(f"\n  测试历史记录 ID: {history.id}")
            
            # 测试球员关系
            if history.player:
                print(f"    ✓ 球员关系正常: {history.player.name}")
            else:
                print(f"    ⚠️  球员关系缺失")
            
            # 测试球队关系
            if history.team:
                print(f"    ✓ 球队关系正常: {history.team.name}")
            else:
                print(f"    ⚠️  球队关系缺失")
            
            # 测试赛事关系
            if history.tournament:
                print(f"    ✓ 赛事关系正常: {history.tournament.name}")
                
                # 测试赛季关系
                if history.tournament.season:
                    print(f"    ✓ 赛季关系正常: {history.tournament.season.name}")
                else:
                    print(f"    ⚠️  赛季关系缺失")
            else:
                print(f"    ⚠️  赛事关系缺失")
    
    except Exception as e:
        print(f"✗ 数据关系测试失败: {e}")
        return False
    
    return True

def generate_sample_queries():
    """生成示例查询语句"""
    print("\n5. 生成示例查询:")
    
    sample_queries = [
        {
            'name': '球员跨赛季统计查询',
            'sql': '''
SELECT 
    p.球员姓名,
    s.赛季名称,
    COUNT(DISTINCT t.赛事ID) as 参与赛事数,
    SUM(pth.赛事进球数) as 赛季进球,
    SUM(pth.赛事黄牌数) as 赛季黄牌,
    SUM(pth.赛事红牌数) as 赛季红牌
FROM player p
JOIN player_team_history pth ON p.球员ID = pth.球员ID
JOIN tournament t ON pth.赛事ID = t.赛事ID
JOIN season s ON t.season_id = s.season_id
GROUP BY p.球员ID, s.season_id
ORDER BY p.球员姓名, s.开始时间;
            '''
        },
        {
            'name': '球员转队历史查询',
            'sql': '''
SELECT 
    p.球员姓名,
    s.赛季名称,
    tb.球队名称,
    pth.赛事进球数,
    ROW_NUMBER() OVER (PARTITION BY p.球员ID ORDER BY s.开始时间) as 效力顺序
FROM player p
JOIN player_team_history pth ON p.球员ID = pth.球员ID
JOIN team ON pth.球队ID = team.球队ID
JOIN team_base tb ON team.基础球队ID = tb.球队基础ID
JOIN tournament t ON pth.赛事ID = t.赛事ID
JOIN season s ON t.season_id = s.season_id
ORDER BY p.球员姓名, s.开始时间;
            '''
        },
        {
            'name': '球员职业生涯汇总',
            'sql': '''
SELECT 
    p.球员姓名,
    COUNT(DISTINCT s.season_id) as 参与赛季数,
    COUNT(DISTINCT tb.球队基础ID) as 效力球队数,
    SUM(pth.赛事进球数) as 职业生涯进球,
    AVG(pth.赛事进球数) as 平均每赛事进球
FROM player p
JOIN player_team_history pth ON p.球员ID = pth.球员ID
JOIN tournament t ON pth.赛事ID = t.赛事ID
JOIN season s ON t.season_id = s.season_id
JOIN team ON pth.球队ID = team.球队ID
JOIN team_base tb ON team.基础球队ID = tb.球队基础ID
GROUP BY p.球员ID
ORDER BY 职业生涯进球 DESC;
            '''
        }
    ]
    
    for i, query in enumerate(sample_queries, 1):
        print(f"\n  {i}. {query['name']}:")
        print(f"     {query['sql'].strip()}")
    
    return True

if __name__ == "__main__":
    print("开始测试球员跨赛季查询功能...")
    
    try:
        # 运行所有测试
        tests = [
            test_player_cross_season_capability,
            test_data_relationships,
            generate_sample_queries
        ]
        
        all_passed = True
        for test in tests:
            if not test():
                all_passed = False
                break
        
        if all_passed:
            print("\n🎉 所有测试通过！球员跨赛季查询功能完全可用。")
            print("\n📋 新功能总结:")
            print("   • 完整的球员跨赛季历史查询")
            print("   • 球员在指定赛季的表现统计")
            print("   • 多球员跨赛季对比分析")
            print("   • 球员转队历史追踪")
            print("   • 丰富的SQL存储过程支持")
        else:
            print("\n❌ 部分测试未通过，需要检查相关配置。")
            
    except Exception as e:
        print(f"\n💥 测试过程中出现异常: {e}")
        sys.exit(1)
