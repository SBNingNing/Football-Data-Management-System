/**
 * 比赛数据映射器 (Match Data Mapper)
 * ------------------------------------------------------------
 * 责任: 将后端返回的原始比赛详情结构(字段命名多为 snake_case, 包含统计聚合数组) 转换为前端视图更易用、语义清晰的对象
 * 目标:
 * 1. 集中字段名称转换，避免组件中充斥 raw.xxx_snake_case
 * 2. 提供默认值 (数值=0 / 文本占位 / 空数组) 保证渲染安全，减少 v-if 判空
 * 3. 若后端新增字段，可在此统一扩展，所有依赖视图自动受益
 *
 * 字段映射概要:
 * - home_team_name -> homeTeam
 * - away_team_name -> awayTeam
 * - home_score / away_score -> homeScore / awayScore
 * - 统计类字段 (home_goals / home_own_goals / ...) -> homeTeamStats | awayTeamStats 分组
 * - players: 数组内字段 player_id -> playerId, player_name -> playerName 等
 * - events: 直接保留 event_type 等原字段, 额外 event_type_text 供 UI 做文本展示
 *
 * 默认值策略:
 * - 字符串: 缺失 -> '' 或 语义占位 ('主队','客队','未知球员','未知球队')
 * - 数值: 缺失/undefined/null -> 0 (利于做加总/展示)
 * - 日期: raw.match_date 不存在 -> null (便于上层基于 null 判断是否显示格式化结果)
 * - 列表: players/events 缺失 -> []
 *
 * 边界与容错:
 * - raw 可能为 undefined: 函数参数默认 {} 保证解构安全
 * - players / events 某个元素字段缺失: 各自 map 内仍套默认值，避免局部崩溃
 * - event_type_text: 后端若未提供, 回退原 event_type 便于至少有可辨识文本
 *
 * 性能说明:
 * - 仅执行一次 O(n) map (n = players + events 数量)；数据量中等可接受。
 * - 若后续存在性能热点，可考虑惰性映射或分页请求层处理。
 *
 * 未来扩展建议:
 * - 新增 derived 字段 (例如 goalDifference = homeScore - awayScore) 时集中在此处计算
 * - 可引入 TypeScript / JSDoc typedef 定义 ViewModel 结构提升 IDE 提示
 */
/**
 * matchMapper
 * 后端比赛数据 -> 视图模型的最小映射集中点，避免各组件散落字段处理。
 * 约定:
 * - 所有可能为空/缺失的数值型字段统一回退 0
 * - 名称缺失回退 "主队" / "客队" / "未知球员" / "未知球队" (保证 UI 不留空)
 * - players/events 保持数组；若后端 null/undefined 用 []
 * 修改指引: 后端新增字段 -> 在此添加并给出默认值，再由组件消费
 */
// 字段分组: 基本信息 / 聚合统计 / 分队统计 / 球员列表 / 事件列表
/**
 * 将原始比赛详情对象转换为前端视图模型
 * @param {Object} raw 后端返回的原始比赛数据对象
 * @returns {Object} 规范化后的视图模型 (字段命名已驼峰化, 含默认值)
 */
export function toMatchViewModel(raw = {}) {
  return {
    id: raw.id,
    homeTeam: raw.home_team_name || '主队',
    awayTeam: raw.away_team_name || '客队',
    homeScore: raw.home_score || 0,
    awayScore: raw.away_score || 0,
    matchDate: raw.match_date || null,
    tournament: raw.competition_name || raw.tournament_name || '',
    season: raw.season_name || '',
    status: raw.status,
    totalGoals: raw.total_goals || 0,
    totalOwnGoals: raw.total_own_goals || 0,
    totalYellowCards: raw.total_yellow_cards || 0,
    totalRedCards: raw.total_red_cards || 0,
    totalPlayers: raw.total_players || 0,
    homeTeamStats: {
      goals: raw.home_goals || 0,
      ownGoals: raw.home_own_goals || 0,
      yellowCards: raw.home_yellow_cards || 0,
      redCards: raw.home_red_cards || 0
    },
    awayTeamStats: {
      goals: raw.away_goals || 0,
      ownGoals: raw.away_own_goals || 0,
      yellowCards: raw.away_yellow_cards || 0,
      redCards: raw.away_red_cards || 0
    },
    players: (raw.players || []).map(p => ({
      playerId: p.player_id,
      playerName: p.player_name || '未知球员',
      teamName: p.team_name || '未知球队',
      playerNumber: p.player_number || 0,
      goals: p.goals || 0,
      ownGoals: p.own_goals || 0,
      yellowCards: p.yellow_cards || 0,
      redCards: p.red_cards || 0
    })),
    events: (raw.events || []).map(e => ({
      id: e.id,
      event_type: e.event_type,
      event_time: e.event_time || 0,
      player_id: e.player_id,
      player_name: e.player_name || '未知球员',
      team_id: e.team_id,
      team_name: e.team_name || '未知球队',
      event_type_text: e.event_type_text || e.event_type
    }))
  };
}
