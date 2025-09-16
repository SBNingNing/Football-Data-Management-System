/**
 * tournamentService (领域: tournament)
 * --------------------------------------------------
 * 聚合赛事历史数据 + 派生统计 (总进球/红黄牌/赛季数/榜单)
 */
import http from '@/utils/httpClient'
import logger from '@/utils/logger'
import { serviceWrap, buildError } from '@/utils/error'

function deriveTotals(records = []) {
  let totalGoals = 0, totalYellow = 0, totalRed = 0
  records.forEach(season => {
    totalGoals += season.totalGoals || 0
    if (Array.isArray(season.teams)) {
      season.teams.forEach(team => {
        totalYellow += team.yellowCards || 0
        totalRed += team.redCards || 0
      })
    }
  })
  return { totalGoals, totalYellowCards: totalYellow, totalRedCards: totalRed }
}

function buildTopLists(records = []) {
  const scorerMap = []
  const cardMap = []
  records.forEach(season => {
    if (!Array.isArray(season.teams)) return
    season.teams.forEach(team => {
      if (!Array.isArray(team.players)) return
      team.players.forEach(p => {
        if (p.goals > 0) {
          scorerMap.push({ ...p, team_name: team.name })
        }
        if ((p.yellowCards || 0) > 0 || (p.redCards || 0) > 0) {
          cardMap.push({ ...p, team_name: team.name })
        }
      })
    })
  })
  const topScorers = scorerMap.sort((a,b)=> (b.goals||0)-(a.goals||0)).slice(0,10)
  const topCards = cardMap.sort((a,b)=> ((b.redCards||0)+(b.yellowCards||0)) - ((a.redCards||0)+(a.yellowCards||0))).slice(0,10)
  return { topScorers, topCards }
}

/**
 * 获取赛事聚合（含派生统计 + 榜单）
 * @param {string} tournamentName
 */
export function fetchTournamentAggregate(tournamentName) {
  return serviceWrap(async () => {
    if (!tournamentName) throw buildError('缺少赛事名称','TOURNAMENT_NAME_MISSING')
    const { ok, data, error } = await http.get(`/tournaments/${encodeURIComponent(tournamentName)}`, {
      cache: { ttl: 30000, key: `tournament:${tournamentName}` }
    })
    if (!ok) throw buildError(error?.message || '获取赛事数据失败','TOURNAMENT_FETCH_FAILED', error)
  if (!(data?.success === true || data?.status === 'success')) throw buildError(data?.message || '获取赛事数据失败','TOURNAMENT_FETCH_INVALID_STATUS', data)

  // 支持 httpClient 解包后结构以及旧 data.data
  const raw = (data?.data && !data.__raw) ? data.data : (data.data || data)
    const records = raw.records || []
    const { totalGoals, totalYellowCards, totalRedCards } = deriveTotals(records)
    const { topScorers, topCards } = buildTopLists(records)
    const result = {
      competition: {
        tournamentName: raw.tournamentName || tournamentName,
        totalSeasons: raw.totalSeasons || records.length,
        totalGoals,
        totalYellowCards,
        totalRedCards,
        records
      },
      topScorers,
      topCards
    }
    logger.debug?.('[tournamentService] fetchTournamentAggregate success', { tournamentName, seasons: result.competition.totalSeasons })
    return result
  })
}
