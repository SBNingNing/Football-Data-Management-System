// playerHistory.js: 球员历史相关接口 -> /api/player-history
import client from './client'

export const fetchPlayerCompleteHistory = (playerId) => client.get(`/player-history/${playerId}/complete`)
export const fetchPlayerSeasonPerformance = (playerId, seasonId) => client.get(`/player-history/${playerId}/season/${seasonId}`)
export const comparePlayersAcrossSeasons = (playerIds, seasonIds=[]) => client.post('/player-history/compare', { player_ids: playerIds, season_ids: seasonIds })
export const fetchPlayerTeamChanges = (playerId) => client.get(`/player-history/team-changes/${playerId}`)
