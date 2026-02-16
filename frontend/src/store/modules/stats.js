// useStatsStore: 综合统计 / 排行榜 / 按赛事统计
import { defineStore } from 'pinia'
import { 
  fetchOverallStats,
  fetchOverallRankings,
  fetchTournamentStats,
  fetchTournamentRanking
} from '@/api/stats'

const OVERALL_TTL = 5000 // 5 秒

export const useStatsStore = defineStore('stats', {
  state: () => ({
    overall: null,
    rankings: null,
    tournamentStats: {},          // { [tournamentId]: data }
    tournamentRankings: {},       // { [tournamentId]: { [type]: data } }
    loading: false,
    error: null,
    lastOverallFetched: 0,
    lastRankingsFetched: 0,
    lastTournamentFetched: {}     // { [tournamentId]: timestamp }
  }),
  actions: {
    _err(e, op){ const msg = e?.message || op + '失败'; this.error = msg; return { success:false, error: msg, statusCode: e?.statusCode } },
    async loadOverall({ force=false } = {}){ const now=Date.now(); if(!force && this.lastOverallFetched && now-this.lastOverallFetched < OVERALL_TTL && this.overall){ return { success:true, data:this.overall, cached:true } } this.loading=true; this.error=null; try{ const r=await fetchOverallStats(); const d=r.data; // httpClient 可能已自动解包，d 可能就是最终数据
        if (d && (d.success === true || d.status === 'success') && Object.prototype.hasOwnProperty.call(d,'data')) {
          this.overall = d.data
        } else {
          this.overall = d
        }
        this.lastOverallFetched=Date.now(); return { success:true, data:this.overall } }catch(e){ return this._err(e,'获取综合统计') } finally { this.loading=false } },
      async loadRankings({ force=false } = {}){ const now=Date.now(); if(!force && this.lastRankingsFetched && now-this.lastRankingsFetched < OVERALL_TTL && this.rankings){ return { success:true, data:this.rankings, cached:true } } this.loading=true; this.error=null; try{ const r=await fetchOverallRankings(); const d=r.data; // httpClient 可能已自动解包，d 可能就是最终数据
          if (d && (d.success === true || d.status === 'success') && Object.prototype.hasOwnProperty.call(d,'data')) {
            this.rankings = d.data
          } else {
            this.rankings = d
          }
          this.lastRankingsFetched=Date.now(); return { success:true, data:this.rankings } }catch(e){ return this._err(e,'获取排行榜') } finally { this.loading=false } },
    async loadTournamentStats(tournamentId, { force=false } = {}){ const now=Date.now(); const key=String(tournamentId); if(!force && this.lastTournamentFetched[key] && now-this.lastTournamentFetched[key] < OVERALL_TTL && this.tournamentStats[key]){ return { success:true, data:this.tournamentStats[key], cached:true } } this.loading=true; this.error=null; try{ const r=await fetchTournamentStats(tournamentId); const d=r.data; if(d?.success===true || d?.status==='success'){ this.tournamentStats[key]=d.data } this.lastTournamentFetched[key]=Date.now(); return { success:true, data:this.tournamentStats[key] } }catch(e){ return this._err(e,'获取赛事统计') } finally { this.loading=false } },
    async loadTournamentRanking(tournamentId, type, { force=false } = {}){ const now=Date.now(); const tKey=String(tournamentId); if(!this.tournamentRankings[tKey]) this.tournamentRankings[tKey] = { meta: { fetched: {} } }; const storeNode=this.tournamentRankings[tKey]; const fetchedMap = storeNode.meta.fetched; const rankKey=type; if(!force && fetchedMap[rankKey] && now - fetchedMap[rankKey] < OVERALL_TTL && storeNode[rankKey]){ return { success:true, data:storeNode[rankKey], cached:true } } this.loading=true; this.error=null; try{ const r=await fetchTournamentRanking(tournamentId, type); const d=r.data; if(d?.success===true || d?.status==='success'){ storeNode[rankKey]=d.data } fetchedMap[rankKey]=Date.now(); return { success:true, data:storeNode[rankKey] } }catch(e){ return this._err(e,'获取赛事排行榜') } finally { this.loading=false } }
  }
})
