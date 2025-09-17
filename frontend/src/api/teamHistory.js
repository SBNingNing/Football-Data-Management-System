// teamHistory.js: 球队历史相关接口 -> /api/team-history
import http from '@/utils/httpClient'

export const fetchTeamCompleteHistory = (teamBaseId) => http.get(`/team-history/${teamBaseId}/complete`)
export const fetchTeamSeasonPerformance = (teamBaseId, seasonId) => http.get(`/team-history/${teamBaseId}/season/${seasonId}`)
export const compareTeamsAcrossSeasons = (teamBaseIds, seasonIds=[]) => http.post('/team-history/compare', { team_base_ids: teamBaseIds, season_ids: seasonIds })
export const fetchTeamTournamentHistory = (teamBaseId) => http.get(`/team-history/tournament-history/${teamBaseId}`)