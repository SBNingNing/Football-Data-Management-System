// stats.js: 综合统计 & 排行榜 -> 后端 /api/stats /api/rankings /api/tournaments/.../stats 等
import http from '@/utils/httpClient'

export const fetchOverallStats = () => http.get('/stats')
export const fetchOverallRankings = () => http.get('/rankings')
export const fetchTournamentStats = (tournamentId) => http.get(`/tournaments/${tournamentId}/stats`)
export const fetchTournamentRanking = (tournamentId, type) => http.get(`/tournaments/${tournamentId}/rankings/${type}`)