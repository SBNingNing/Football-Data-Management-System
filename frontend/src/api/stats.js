// stats.js: 综合统计 & 排行榜 -> 后端 /api/stats /api/rankings /api/tournaments/.../stats 等
import client from './client'

export const fetchOverallStats = () => client.get('/stats')
export const fetchOverallRankings = () => client.get('/rankings')
export const fetchTournamentStats = (tournamentId) => client.get(`/tournaments/${tournamentId}/stats`)
export const fetchTournamentRanking = (tournamentId, type) => client.get(`/tournaments/${tournamentId}/rankings/${type}`)
