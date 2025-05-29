import api from './api'

const playerService = {
  getAllPlayers() {
    return api.get('/players')
  },

  getPlayerById(id) {
    return api.get(`/players/${id}`)
  },

  createPlayer(playerData) {
    return api.post('/players', playerData)
  },

  updatePlayer(id, playerData) {
    return api.put(`/players/${id}`, playerData)
  },

  deletePlayer(id) {
    return api.delete(`/players/${id}`)
  },

  getPlayersByTeam(teamId) {
    return api.get(`/players/team/${teamId}`)
  },

  getPlayersBySeason(seasonId) {
    return api.get(`/players/season/${seasonId}`)
  },

  getPlayersByTeamAndSeason(teamId, seasonId) {
    return api.get(`/players/team/${teamId}/season/${seasonId}`)
  }
}

export default playerService
