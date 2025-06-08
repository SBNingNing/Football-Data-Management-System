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
    // 初始化方法 - 应用启动时调用
    init() {
      if (this.token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
      }
    },

    // 统一的数据处理方法
    _handleApiResponse(response, dataType = 'data') {
      console.log(`获取${dataType}响应:`, response.data);
      
      if (response.data && response.data.status === 'success') {
        return Array.isArray(response.data.data) ? response.data.data : [];
      } else if (Array.isArray(response.data)) {
        return response.data;
      } else {
        console.warn(`${dataType}格式异常:`, response.data);
        return [];
      }
    },

    // 统一的错误处理方法
    _handleApiError(error, operation) {
      console.error(`${operation}失败:`, error);
      
      // 如果是401错误，清除token并跳转到登录页
      if (error.response?.status === 401) {
        this.logout()
        // 可以在这里添加跳转到登录页的逻辑
        const errorMessage = '登录已过期，请重新登录'
        this.error = errorMessage
        return { success: false, error: errorMessage }
      }
      
      const errorMessage = error.response?.data?.message || `${operation}失败`;
      this.error = errorMessage;
      return { success: false, error: errorMessage };
    },

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
        const response = await axios.post('/api/teams', teamData)
        this.loading = false
        
        if (response.data.status === 'success') {
          await this.fetchTeams() // 刷新球队列表
          return { success: true, data: response.data }
        }
        return { success: false, error: response.data.message }
      } catch (error) {
        this.loading = false
        return this._handleApiError(error, '创建球队')
      }
    },
    
    async fetchTeams() {
      this.loading = true
      this.error = null
      
      try {
        console.log('正在获取球队数据...');
        const response = await axios.get('/api/teams')
        console.log('球队API响应:', response);
        
        const teamsData = this._handleApiResponse(response, '球队数据')
        console.log('处理后的球队数据:', teamsData);
        
        this.teams = teamsData
        this.loading = false
        return { success: true, data: teamsData }
      } catch (error) {
        console.error('获取球队数据失败:', error);
        this.loading = false
        this.teams = [] // 确保出错时清空数据
        return this._handleApiError(error, '获取球队列表')
      }
    },
    
    async updateTeam(teamId, teamData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.put(`/api/teams/${teamId}`, teamData)
        this.loading = false
        
        if (response.data.status === 'success') {
          await this.fetchTeams() // 刷新球队列表
          return { success: true, data: response.data }
        }
        return { success: false, error: response.data.message }
      } catch (error) {
        this.loading = false
        return this._handleApiError(error, '更新球队')
      }
    },
    
    async deleteTeam(teamId) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.delete(`/api/teams/${teamId}`)
        this.loading = false
        
        if (response.data.status === 'success') {
          await this.fetchTeams() // 刷新球队列表
          return { success: true, data: response.data }
        }
        return { success: false, error: response.data.message }
      } catch (error) {
        this.loading = false
        return this._handleApiError(error, '删除球队')
      }
    },
    
    async fetchPlayers() {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get('/api/players')
        const playersData = this._handleApiResponse(response, '球员数据')
        
        this.players = playersData
        this.loading = false
        return { success: true, data: playersData }
      } catch (error) {
        this.loading = false
        this.players = [] // 确保出错时清空数据
        return this._handleApiError(error, '获取球员列表')
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
        this.loading = false
        return this._handleApiError(error, '创建比赛')
      }
    },
    
    async fetchMatches() {
      this.loading = true
      this.error = null
      
      try {
        // 确保请求前token已设置
        if (this.token && !axios.defaults.headers.common['Authorization']) {
          axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        }
        
        const response = await axios.get('/api/matches')
        const matchesData = this._handleApiResponse(response, '比赛数据')
        
        this.matches = matchesData
        this.loading = false
        return { success: true, data: matchesData }
      } catch (error) {
        this.loading = false
        this.matches = [] // 确保出错时清空数据
        return this._handleApiError(error, '获取比赛列表')
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
        this.loading = false
        return this._handleApiError(error, '更新比赛')
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
        this.loading = false
        return this._handleApiError(error, '删除比赛')
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
        this.loading = false
        return this._handleApiError(error, '创建事件')
      }
    },
    
    async fetchEvents() {
      this.loading = true
      this.error = null
      
      try {
        console.log('正在获取事件数据...');
        const response = await axios.get('/api/events')
        console.log('事件API响应:', response);
        
        const eventsData = this._handleApiResponse(response, '事件数据')
        console.log('处理后的事件数据:', eventsData);
        
        this.events = eventsData
        this.loading = false
        return { success: true, data: eventsData }
      } catch (error) {
        console.error('获取事件数据失败:', error);
        console.error('错误详情:', error.response?.data);
        
        this.loading = false
        this.events = [] // 确保出错时清空数据
        
        // 提供更详细的错误信息
        const errorMessage = error.response?.data?.message || 
                           error.response?.data?.error || 
                           '获取事件列表失败';
        
        return { success: false, error: errorMessage }
      }
    },
    
    async updateEvent(eventId, eventData) {
      this.loading = true
      this.error = null
      
      try {
        console.log('正在更新事件:', eventId, eventData);
        const response = await axios.put(`/api/events/${eventId}`, eventData)
        console.log('更新事件响应:', response);
        
        this.loading = false
        
        if (response.data.status === 'success') {
          // 更新成功后重新获取事件列表
          await this.fetchEvents()
          return { success: true, data: response.data }
        }
        return { success: false, error: response.data.message }
      } catch (error) {
        console.error('更新事件失败:', error);
        console.error('错误详情:', error.response?.data);
        
        this.loading = false
        
        const errorMessage = error.response?.data?.message || 
                           error.response?.data?.error || 
                           '更新事件失败';
        
        return { success: false, error: errorMessage }
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
        this.loading = false
        return this._handleApiError(error, '删除事件')
      }
    },
    
    async createPlayer(playerData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post('/api/players', playerData)
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
        const response = await axios.put(`/api/players/${playerId}`, playerData)
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
        const response = await axios.delete(`/api/players/${playerId}`)
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

    async fetchPlayerById(playerId) {
      this.loading = true
      this.error = null
      
      try {
        console.log('正在获取球员详情:', playerId);
        const response = await axios.get(`/api/players/${playerId}`)
        console.log('球员详情API响应:', response);
        
        this.loading = false
        
        if (response.data && response.data.status === 'success') {
          return { success: true, data: response.data.data }
        } else {
          const errorMessage = response.data?.message || '获取球员详情失败'
          console.error('API返回错误:', errorMessage);
          return { success: false, error: errorMessage }
        }
      } catch (error) {
        console.error('获取球员详情失败:', error);
        this.loading = false
        
        const errorMessage = error.response?.data?.message || 
                           error.response?.data?.error || 
                           '网络错误，无法获取球员详情';
        
        return { success: false, error: errorMessage }
      }
    }
  }
})
