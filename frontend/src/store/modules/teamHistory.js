// useTeamHistoryStore: 球队历史（完整 / 赛季表现 / 对比 / 赛事参赛）
import { defineStore } from 'pinia'
import {
  fetchTeamCompleteHistory,
  fetchTeamSeasonPerformance,
  compareTeamsAcrossSeasons,
  fetchTeamTournamentHistory
} from '@/api/teamHistory'

const TTL_COMPLETE = 30000
const TTL_SEASON = 15000
const TTL_TOURNAMENT = 30000

export const useTeamHistoryStore = defineStore('teamHistory', {
  state: () => ({
    completeCache: {},
    seasonPerfCache: {},
    tournamentHistCache: {},
    lastCompleteFetched: {},
    lastSeasonFetched: {},
    lastTournamentHistFetched: {},
    compareResult: null,
    loading: false,
    error: null
  }),
  actions: {
    _err(e, op) {
      const msg = e?.message || op + '失败'
      this.error = msg
      return { success: false, error: msg, statusCode: e?.statusCode }
    },

    async loadComplete(team_base_id, { force = false } = {}) {
      const now = Date.now()
      const ts = this.lastCompleteFetched[team_base_id]
      if (!force && ts && now - ts < TTL_COMPLETE && this.completeCache[team_base_id]) {
        return { success: true, data: this.completeCache[team_base_id], cached: true }
      }
      this.loading = true
      this.error = null
      try {
        const r = await fetchTeamCompleteHistory(team_base_id)
        if (r.ok) {
          const d = r.data
          this.completeCache[team_base_id] = d
          this.lastCompleteFetched[team_base_id] = Date.now()
          return { success: true, data: d }
        }
        return { success: false, error: r.error?.message || '请求失败' }
      } catch (e) {
        return this._err(e, '获取球队完整历史')
      } finally {
        this.loading = false
      }
    },

    async loadSeasonPerformance(team_base_id, season_id, { force = false } = {}) {
      const now = Date.now()
      if (!this.lastSeasonFetched[team_base_id]) this.lastSeasonFetched[team_base_id] = {}
      if (!this.seasonPerfCache[team_base_id]) this.seasonPerfCache[team_base_id] = {}
      
      const ts = this.lastSeasonFetched[team_base_id][season_id]
      const cachedData = this.seasonPerfCache[team_base_id][season_id]
      
      if (!force && ts && now - ts < TTL_SEASON && cachedData) {
        return { success: true, data: cachedData, cached: true }
      }
      
      this.loading = true
      this.error = null
      try {
        const r = await fetchTeamSeasonPerformance(team_base_id, season_id)
        if (r.ok) {
          const d = r.data
          this.seasonPerfCache[team_base_id][season_id] = d
          this.lastSeasonFetched[team_base_id][season_id] = Date.now()
          return { success: true, data: d }
        }
        return { success: false, error: r.error?.message || '请求失败' }
      } catch (e) {
        return this._err(e, '获取球队赛季表现')
      } finally {
        this.loading = false
      }
    },

    async loadTournamentHistory(team_base_id, { force = false } = {}) {
      const now = Date.now()
      const ts = this.lastTournamentHistFetched[team_base_id]
      if (!force && ts && now - ts < TTL_TOURNAMENT && this.tournamentHistCache[team_base_id]) {
        return { success: true, data: this.tournamentHistCache[team_base_id], cached: true }
      }
      this.loading = true
      this.error = null
      try {
        const r = await fetchTeamTournamentHistory(team_base_id)
        if (r.ok) {
          const d = r.data
          this.tournamentHistCache[team_base_id] = d
          this.lastTournamentHistFetched[team_base_id] = Date.now()
          return { success: true, data: d }
        }
        return { success: false, error: r.error?.message || '请求失败' }
      } catch (e) {
        return this._err(e, '获取球队参赛历史')
      } finally {
        this.loading = false
      }
    },

    async compare(team_base_ids, season_ids = []) {
      this.loading = true
      this.error = null
      try {
        const r = await compareTeamsAcrossSeasons(team_base_ids, season_ids)
        if (r.ok) {
          this.compareResult = r.data
          return { success: true, data: r.data }
        }
        return { success: false, error: r.error?.message || '请求失败' }
      } catch (e) {
        return this._err(e, '球队对比')
      } finally {
        this.loading = false
      }
    }
  }
})
