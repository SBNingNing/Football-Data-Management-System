/**
 * teamHistoryMapper
 * 统一球队历史/统计字段，兼容旧命名；提供按需派生字段。
 * 规则: 优先新 -> 旧别名 -> 计算派生。
 * 派生: totalGoalDifference 若缺失则用 (totalGoals - totalGoalsConceded).
 * 修改: 后端新增统计时在此追加，减少组件判断。
 */
// 字段: teamName / totals(Goals,Conceded,GoalDifference,Yellow,Red,Points) / bestRank / records
export function toTeamHistoryViewModel(raw = {}, teamName) {
  // 如果 raw 包含 teamInfo，使用 teamInfo 中的信息
  const teamInfo = raw.team_info || raw.teamInfo || {}
  const actualTeamName = teamInfo.name || teamInfo.teamName || raw.teamName || raw.name || teamName || '未知球队'
  
  const summary = raw.career_summary || {}
  
  // 将 seasons 结构展平为 records (tournaments)
  let records = []
  if (raw.seasons && Array.isArray(raw.seasons)) {
      raw.seasons.forEach(seasonBlock => {
          if (seasonBlock.tournaments && Array.isArray(seasonBlock.tournaments)) {
              seasonBlock.tournaments.forEach(t => {
                  records.push({
                      id: t.team_id, // participation ID
                      tournamentId: t.tournament_id,
                      tournamentName: t.tournament_name,
                      matchType: t.competition_name,
                      rank: t.final_ranking,
                      goals: t.stats ? t.stats.total_goals : 0,
                      goalsConceded: t.stats ? t.stats.total_goals_conceded : 0,
                      goalDifference: t.stats ? t.stats.total_goal_difference : 0,
                      yellowCards: t.stats ? t.stats.total_yellow_cards : 0,
                      redCards: t.stats ? t.stats.total_red_cards : 0,
                      players: t.players || [] // 从后端获取球员列表
                  })
              })
          }
      })
  } else if (raw.records || raw.tournaments) {
      records = raw.records || raw.tournaments
  }

  return {
    teamName: actualTeamName,
    teamBaseId: teamInfo.id || teamInfo.teamBaseId || raw.teamBaseId,
    totalGoals: summary.total_goals_scored || raw.totalGoals || raw.goals || 0,
    totalGoalsConceded: summary.total_goals_conceded || raw.totalGoalsConceded || raw.goalsConceded || 0,
    totalGoalDifference: summary.total_goal_difference || raw.totalGoalDifference || raw.goalDifference || 0,
    totalYellowCards: summary.total_yellow_cards || raw.totalYellowCards || raw.yellowCards || 0,
    totalRedCards: summary.total_red_cards || raw.totalRedCards || raw.redCards || 0,
    totalPoints: summary.total_points || raw.totalPoints || raw.points || 0,
    bestRank: summary.best_ranking || raw.bestRank || raw.best_rank || null,
    records: records
  };
}
