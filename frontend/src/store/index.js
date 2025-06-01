import { defineStore } from 'pinia'
import axios from 'axios'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    loading: false,
    error: null
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
    
    logout() {
      this.user = null
      this.token = null
      
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
    }
  }
})
