// statsService: 汇总首页/统计页相关多接口访问，统一字段映射与错误处理
// 提供：fetchDashboardStats, fetchRankings （已移除不存在的 groupRankings / playoffBracket 真实接口，改为占位）
// NOTE: 比赛相关方法已迁移至 domain/match/matchService
import http from '@/utils/httpClient'
import { serviceWrap, buildError } from '@/utils/error'

export async function fetchDashboardStats({ token, force = false } = {}) {
  return serviceWrap(async () => {
    const headers = token ? { Authorization: `Bearer ${token}` } : undefined
    const res = await http.get('/stats', { headers, cache: { ttl: 10000, force } })
    if (!res.ok) {
      throw buildError(res.error?.message || '获取统计数据失败', 'STATS_FETCH_FAILED', res.error)
    }
  const d = res.data || {}
    return {
      totalMatches: d.totalMatches || 0,
      upcomingMatches: d.upcomingMatches || 0,
      completedMatches: d.completedMatches || 0
    }
  })
}

// 占位：后端无 /group-rankings，返回空结构，避免调用端崩溃
export function fetchGroupRankingsPlaceholder() {
  return serviceWrap(async () => ({ groups: [] }))
}

// 占位：后端无 /playoff-bracket
export function fetchPlayoffBracketPlaceholder() {
  return serviceWrap(async () => ({ rounds: [] }))
}

// 为兼容旧调用名称，导出别名函数（可以后续在调用端逐步迁移到 *Placeholder 命名）
export const fetchGroupRankings = fetchGroupRankingsPlaceholder
export const fetchPlayoffBracket = fetchPlayoffBracketPlaceholder

// 排行榜综合：返回 { championsCup, womensCup, eightASide }
export async function fetchRankings({ token, force = false, season_id } = {}) {
  return serviceWrap(async () => {
    const headers = token ? { Authorization: `Bearer ${token}` } : undefined
    const params = {}
    if (season_id) params.season_id = season_id
    
    const res = await http.get('/stats/rankings', { headers, params, cache: { ttl: 15000, force } })
    if (!res.ok) throw buildError(res.error?.message || '获取排行榜失败', 'RANKINGS_FETCH_FAILED', res.error)
  return res.data || {}
  })
}

function mapPlayer(player, fallbackPrefix) {
  return {
    id: player.id || player.player_id || `${fallbackPrefix}_${Math.random().toString(36).slice(2,8)}`,
    name: player.name || player.player_name || '未知球员',
    teamName: player.teamName || player.team_name || '未知队伍',
    goals: player.goals || 0,
    yellowCards: player.yellowCards || player.yellow_cards || 0,
    redCards: player.redCards || player.red_cards || 0,
    totalCards: player.totalCards || player.total_cards || 0,
    ...player
  }
}

export function processRankingDataBlock(competitionData, _competitionName) {
  const defaultRankingData = { topScorers: { players: [], teams: [] }, cards: { players: [], teams: [] }, points: [] }
  if (!competitionData) return { ...defaultRankingData }
  return {
    topScorers: {
      players: Array.isArray(competitionData.topScorers?.players) ? competitionData.topScorers.players.map(p=>mapPlayer(p,'射手')) : [],
      teams: competitionData.topScorers?.teams || []
    },
    cards: {
      players: Array.isArray(competitionData.cards?.players) ? competitionData.cards.players.map(p=>mapPlayer(p,'红黄牌')) : [],
      teams: competitionData.cards?.teams || []
    },
    points: competitionData.points || []
  }
}
