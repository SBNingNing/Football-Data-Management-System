import { defineStore } from 'pinia'
import { fetchSeasons } from '@/api/seasons'
import { fetchCompetitions } from '@/api/competitions'

export const useMetaStore = defineStore('meta', {
  state: () => ({
    seasons: [],
    competitions: [],
    loading: false,
    lastFetch: {
      seasons: 0,
      competitions: 0
    }
  }),
  getters: {
    getSeasonById: (state) => (id) => state.seasons.find(s => s.id === id),
    getCompetitionById: (state) => (id) => state.competitions.find(c => c.id === id),
    seasonOptions: (state) => state.seasons.map(s => ({ label: s.name, value: s.id })),
    competitionOptions: (state) => state.competitions.map(c => ({ label: c.name, value: c.id }))
  },
  actions: {
    async loadSeasons(force = false) {
      // 简单的缓存策略：如果有数据且未过期（5分钟），则不重新请求
      if (!force && this.seasons.length > 0 && (Date.now() - this.lastFetch.seasons < 300000)) {
        return
      }
      try {
        const res = await fetchSeasons()
        // 兼容不同的响应结构
        const rawData = res.data || res
        const list = Array.isArray(rawData) ? rawData : (rawData.data || [])
        this.seasons = list
        this.lastFetch.seasons = Date.now()
      } catch (e) {
        console.error('Failed to load seasons', e)
      }
    },
    async loadCompetitions(force = false) {
      if (!force && this.competitions.length > 0 && (Date.now() - this.lastFetch.competitions < 300000)) {
        return
      }
      try {
        const res = await fetchCompetitions()
        const rawData = res.data || res
        // 兼容 { competitions: [...] } 或 [...]
        const list = Array.isArray(rawData) ? rawData : (rawData.competitions || rawData.data || [])
        this.competitions = list
        this.lastFetch.competitions = Date.now()
      } catch (e) {
        console.error('Failed to load competitions', e)
      }
    },
    async loadAll(force = false) {
        this.loading = true
        await Promise.all([this.loadSeasons(force), this.loadCompetitions(force)])
        this.loading = false
    }
  }
})
