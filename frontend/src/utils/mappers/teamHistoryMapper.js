/**
 * teamHistoryMapper
 * 统一球队历史/统计字段，兼容旧命名；提供按需派生字段。
 * 规则: 优先新 -> 旧别名 -> 计算派生。
 * 派生: totalGoalDifference 若缺失则用 (totalGoals - totalGoalsConceded).
 * 修改: 后端新增统计时在此追加，减少组件判断。
 */
// 字段: teamName / totals(Goals,Conceded,GoalDifference,Yellow,Red,Points) / bestRank / records
export function toTeamHistoryViewModel(raw = {}, teamName) {
  return {
    teamName: raw.teamName || raw.name || teamName || '未知球队',
    totalGoals: raw.totalGoals || raw.goals || 0,
    totalGoalsConceded: raw.totalGoalsConceded || raw.goalsConceded || 0,
    totalGoalDifference: raw.totalGoalDifference || raw.goalDifference || ((raw.totalGoals||0)-(raw.totalGoalsConceded||0)),
    totalYellowCards: raw.totalYellowCards || raw.yellowCards || 0,
    totalRedCards: raw.totalRedCards || raw.redCards || 0,
    totalPoints: raw.totalPoints || raw.points || 0,
    bestRank: raw.bestRank || raw.best_rank || null,
    records: raw.records || raw.tournaments || []
  };
}
