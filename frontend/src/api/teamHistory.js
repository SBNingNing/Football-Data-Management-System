// teamHistory.js: 球队历史相关接口 -> /api/team-history
import client from './client'

export const fetchTeamCompleteHistory = (teamBaseId) => client.get(`/team-history/${teamBaseId}/complete`)
export const fetchTeamSeasonPerformance = (teamBaseId, seasonId) => client.get(`/team-history/${teamBaseId}/season/${seasonId}`)
export const compareTeamsAcrossSeasons = (teamBaseIds, seasonIds=[]) => client.post('/team-history/compare', { team_base_ids: teamBaseIds, season_ids: seasonIds })
export const fetchTeamTournamentHistory = (teamBaseId) => client.get(`/team-history/tournament-history/${teamBaseId}`)
