import { defineStore } from 'pinia'
import axios from 'axios'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    loading: false,
    error: null,
    teams: [],
    players: [],
    matches: [],
    events: []
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token,
    currentUser: (state) => state.user
  },
  
  actions: {
    async login(credentials) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post('/api/auth/login', credentials)
        const { access_token, user } = response.data
        
        this.token = access_token
        this.user = user
        
        localStorage.setItem('token', access_token)
        
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        
        this.loading = false
        return true
      } catch (error) {
        this.error = error.response?.data?.error || '登录失败'
        this.loading = false
        return false
      }
    },
    
    async register(userData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post('/api/auth/register', userData)
        this.loading = false
        return true
      } catch (error) {
        this.error = error.response?.data?.error || '注册失败'
        this.loading = false
        return false
      }
    },
    
    async setGuestMode() {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post('/api/auth/guest-login')
        const { access_token } = response.data
        
        this.token = access_token
        this.user = { role: 'guest' }
        
        localStorage.setItem('token', access_token)
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        
        this.loading = false
        return true
      } catch (error) {
        this.error = error.response?.data?.error || '游客登录失败'
        this.loading = false
        return false
      }
    },
    
    async adminLogin(credentials) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post('/api/auth/login', credentials)
        const { access_token, user } = response.data
        
        this.token = access_token
        this.user = { ...user, role: 'admin' }
        
        localStorage.setItem('token', access_token)
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        
        this.loading = false
        return true
      } catch (error) {
        this.error = error.response?.data?.error || '管理员登录失败'
        this.loading = false
        return false
      }
    },
    
    logout() {
      this.user = null
      this.token = null
      
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
    },
    
    async createTeam(teamData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post('/api/auth/teams', teamData)
        this.loading = false
        
        if (response.data.status === 'success') {
          await this.fetchTeams() // 刷新球队列表
          return { success: true, data: response.data }
        }
        return { success: false, error: response.data.message }
      } catch (error) {
        this.error = error.response?.data?.message || '创建球队失败'
        this.loading = false
        return { success: false, error: this.error }
      }
    },
    
    async fetchTeams() {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get('/api/teams')
        
        if (response.data.status === 'success') {
          this.teams = response.data.data
        }
        
        this.loading = false
        return { success: true, data: response.data.data }
      } catch (error) {
        this.error = error.response?.data?.message || '获取球队列表失败'
        this.loading = false
        return { success: false, error: this.error }
      }
    },
    
    async updateTeam(teamId, teamData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.put(`/api/auth/teams/${teamId}`, teamData)
        this.loading = false
        
        if (response.data.status === 'success') {
          await this.fetchTeams() // 刷新球队列表
          return { success: true, data: response.data }
        }
        return { success: false, error: response.data.message }
      } catch (error) {
        this.error = error.response?.data?.message || '更新球队失败'
        this.loading = false
        return { success: false, error: this.error }
      }
    },
    
    async deleteTeam(teamId) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.delete(`/api/auth/teams/${teamId}`)
        this.loading = false
        
        if (response.data.status === 'success') {
          await this.fetchTeams() // 刷新球队列表
          return { success: true, data: response.data }
        }
        return { success: false, error: response.data.message }
      } catch (error) {
        this.error = error.response?.data?.message || '删除球队失败'
        this.loading = false
        return { success: false, error: this.error }
      }
    },
    
    async fetchPlayers() {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get('/api/players')
        
        if (response.data.status === 'success') {
          this.players = response.data.data
        }
        
        this.loading = false
        return { success: true, data: response.data.data }
      } catch (error) {
        this.error = error.response?.data?.message || '获取球员列表失败'
        this.loading = false
        return { success: false, error: this.error }
      }
    },
    
    async createMatch(matchData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post('/api/matches', matchData)
        this.loading = false
        
        if (response.data.status === 'success') {
          await this.fetchMatches()
          return { success: true, data: response.data }
        }
        return { success: false, error: response.data.message }
      } catch (error) {
        this.error = error.response?.data?.message || '创建比赛失败'
        this.loading = false
        return { success: false, error: this.error }
      }
    },
    
    async fetchMatches() {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get('/api/matches')
        
        if (response.data.status === 'success') {
          this.matches = response.data.data
        }
        
        this.loading = false
        return { success: true, data: response.data.data }
      } catch (error) {
        this.error = error.response?.data?.message || '获取比赛列表失败'
        this.loading = false
        return { success: false, error: this.error }
      }
    },
    
    async updateMatch(matchId, matchData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.put(`/api/matches/${matchId}`, matchData)
        this.loading = false
        
        if (response.data.status === 'success') {
          await this.fetchMatches()
          return { success: true, data: response.data }
        }
        return { success: false, error: response.data.message }
      } catch (error) {
        this.error = error.response?.data?.message || '更新比赛失败'
        this.loading = false
        return { success: false, error: this.error }
      }
    },
    
    async deleteMatch(matchId) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.delete(`/api/matches/${matchId}`)
        this.loading = false
        
        if (response.data.status === 'success') {
          await this.fetchMatches()
          return { success: true, data: response.data }
        }
        return { success: false, error: response.data.message }
      } catch (error) {
        this.error = error.response?.data?.message || '删除比赛失败'
        this.loading = false
        return { success: false, error: this.error }
      }
    },
    
    async createEvent(eventData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post('/api/events', eventData)
        this.loading = false
        
        if (response.data.status === 'success') {
          await this.fetchEvents()
          return { success: true, data: response.data }
        }
        return { success: false, error: response.data.message }
      } catch (error) {
        this.error = error.response?.data?.message || '创建事件失败'
        this.loading = false
        return { success: false, error: this.error }
      }
    },
    
    async fetchEvents() {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get('/api/events')
        
        if (response.data.status === 'success') {
          this.events = response.data.data
        }
        
        this.loading = false
        return { success: true, data: response.data.data }
      } catch (error) {
        this.error = error.response?.data?.message || '获取事件列表失败'
        this.loading = false
        return { success: false, error: this.error }
      }
    },
    
    async updateEvent(eventId, eventData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.put(`/api/events/${eventId}`, eventData)
        this.loading = false
        
        if (response.data.status === 'success') {
          await this.fetchEvents()
          return { success: true, data: response.data }
        }
        return { success: false, error: response.data.message }
      } catch (error) {
        this.error = error.response?.data?.message || '更新事件失败'
        this.loading = false
        return { success: false, error: this.error }
      }
    },
    
    async deleteEvent(eventId) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.delete(`/api/events/${eventId}`)
        this.loading = false
        
        if (response.data.status === 'success') {
          await this.fetchEvents()
          return { success: true, data: response.data }
        }
        return { success: false, error: response.data.message }
      } catch (error) {
        this.error = error.response?.data?.message || '删除事件失败'
        this.loading = false
        return { success: false, error: this.error }
      }
    },
    
    async createPlayer(playerData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post('/api/auth/players', playerData)
        this.loading = false
        
        if (response.data.status === 'success') {
          await this.fetchPlayers()
          return { success: true, data: response.data }
        }
        return { success: false, error: response.data.message }
      } catch (error) {
        this.error = error.response?.data?.message || '创建球员失败'
        this.loading = false
        return { success: false, error: this.error }
      }
    },
    
    async updatePlayer(playerId, playerData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.put(`/api/auth/players/${playerId}`, playerData)
        this.loading = false
        
        if (response.data.status === 'success') {
          await this.fetchPlayers()
          return { success: true, data: response.data }
        }
        return { success: false, error: response.data.message }
      } catch (error) {
        this.error = error.response?.data?.message || '更新球员失败'
        this.loading = false
        return { success: false, error: this.error }
      }
    },
    
    async deletePlayer(playerId) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.delete(`/api/auth/players/${playerId}`)
        this.loading = false
        
        if (response.data.status === 'success') {
          await this.fetchPlayers()
          return { success: true, data: response.data }
        }
        return { success: false, error: response.data.message }
      } catch (error) {
        this.error = error.response?.data?.message || '删除球员失败'
        this.loading = false
        return { success: false, error: this.error }
      }
    },
  }
})
