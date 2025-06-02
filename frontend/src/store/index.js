import { defineStore } from 'pinia'
import axios from 'axios'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    loading: false,
    error: null,
    teams: [],
    players: []
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
        const response = await axios.get('/api/auth/teams')
        
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
        const response = await axios.get('/api/auth/players')
        
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
  }
})
