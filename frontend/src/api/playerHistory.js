// playerHistory.js: 球员历史相关接口 -> /api/player-history
import http from '@/utils/httpClient'

export const fetchPlayerCompleteHistory = (playerId) => http.get(`/player-history/${playerId}/complete`)
export const fetchPlayerSeasonPerformance = (playerId, seasonId) => http.get(`/player-history/${playerId}/season/${seasonId}`)
export const comparePlayersAcrossSeasons = (playerIds, seasonIds=[]) => http.post('/player-history/compare', { player_ids: playerIds, season_ids: seasonIds })
export const fetchPlayerTeamChanges = (playerId) => http.get(`/player-history/team-changes/${playerId}`)