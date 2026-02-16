// teamHistory.js: 球队历史相关接口 -> /api/team-history
import http from '@/utils/httpClient'

export const fetchTeamCompleteHistory = (team_base_id) => http.get(`/team-history/${team_base_id}/complete`)
export const fetchTeamSeasonPerformance = (team_base_id, season_id) => http.get(`/team-history/${team_base_id}/season/${season_id}`)
export const compareTeamsAcrossSeasons = (team_base_ids, season_ids=[]) => http.post('/team-history/compare', { team_base_ids, season_ids })
export const fetchTeamTournamentHistory = (team_base_id) => http.get(`/team-history/tournament-history/${team_base_id}`)