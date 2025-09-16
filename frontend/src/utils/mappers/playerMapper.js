/**
 * playerMapper
 * 用于将后端(存在字段别名/历史兼容)的球员历史数据统一到视图模型。
 * 策略: 优先新字段 -> 兼容旧/别名 -> 默认值。
 * 修改: 后端新增统计字段时在此添加，避免组件散落判断。
 */
// 字段说明: name/studentId/currentTeam/当前赛事赛季/号码/生涯统计/赛季数组/球队履历数组
export function toPlayerHistoryViewModel(raw = {}, playerId) {
  // 兼容两种形态：
  // A) 后端 player_history_service 返回: { player_info, seasons, career_summary }
  // B) 旧形态/其他接口: 平铺字段
  const info = raw.player_info || raw
  const career = raw.career_summary || raw
  return {
    name: info.name || info.player_name || '未知球员',
    studentId: info.id || playerId,
    currentTeam: info.team_name || info.current_team || '暂无队伍',
    currentTournament: info.tournament_name || info.current_tournament || '暂无赛事',
    currentSeason: info.season_name || info.current_season || '暂无赛季',
    matchType: info.matchType || info.match_type || 'champions-cup',
    playerNumber: info.player_number || info.number || 0,
    totalGoals: career.total_goals || career.career_goals || 0,
    totalYellowCards: career.total_yellow_cards || career.career_yellow_cards || 0,
    totalRedCards: career.total_red_cards || career.career_red_cards || 0,
    seasons: raw.seasons || raw.season_performance || [],
    teamHistories: raw.team_histories || raw.teamHistories || []
  }
}
