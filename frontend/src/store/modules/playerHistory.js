// usePlayerHistoryStore: 球员历史（完整 / 赛季表现 / 对比 / 转队）
import { defineStore } from 'pinia'
import { 
  fetchPlayerCompleteHistory,
  fetchPlayerSeasonPerformance,
  comparePlayersAcrossSeasons,
  fetchPlayerTeamChanges
} from '@/api/playerHistory'

const TTL_COMPLETE = 30000
const TTL_SEASON = 15000
const TTL_TRANSFERS = 30000

export const usePlayerHistoryStore = defineStore('playerHistory', {
  state: () => ({
    completeCache: {},          // playerId -> data
    seasonPerfCache: {},        // playerId -> { seasonId -> data }
    transfersCache: {},         // playerId -> data
    lastCompleteFetched: {},    // playerId -> ts
    lastSeasonFetched: {},      // playerId -> { seasonId -> ts }
    lastTransfersFetched: {},   // playerId -> ts
    compareResult: null,
    loading: false,
    error: null
  }),
  actions: {
    _err(e, op){ const msg=e?.message||op+'失败'; this.error=msg; return {success:false,error:msg,statusCode:e?.statusCode} },
    async loadComplete(playerId,{force=false}={}){ const now=Date.now(); const ts=this.lastCompleteFetched[playerId]; if(!force && ts && now-ts<TTL_COMPLETE && this.completeCache[playerId]) return {success:true,data:this.completeCache[playerId],cached:true}; this.loading=true; this.error=null; try{ const r=await fetchPlayerCompleteHistory(playerId); const d=r.data; if(d?.success===true || d?.status==='success'){ this.completeCache[playerId]=d.data; this.lastCompleteFetched[playerId]=Date.now(); return {success:true,data:d.data}; } return {success:false,error:d?.message}; }catch(e){ return this._err(e,'获取球员完整历史'); } finally { this.loading=false } },
    async loadSeasonPerformance(playerId,seasonId,{force=false}={}){ const now=Date.now(); if(!this.lastSeasonFetched[playerId]) this.lastSeasonFetched[playerId]={}; if(!this.seasonPerfCache[playerId]) this.seasonPerfCache[playerId]={}; const ts=this.lastSeasonFetched[playerId][seasonId]; const cachedData=this.seasonPerfCache[playerId][seasonId]; if(!force && ts && now-ts<TTL_SEASON && cachedData) return {success:true,data:cachedData,cached:true}; this.loading=true; this.error=null; try{ const r=await fetchPlayerSeasonPerformance(playerId,seasonId); const d=r.data; if(d?.success===true || d?.status==='success'){ this.seasonPerfCache[playerId][seasonId]=d.data; this.lastSeasonFetched[playerId][seasonId]=Date.now(); return {success:true,data:d.data}; } return {success:false,error:d?.message}; }catch(e){ return this._err(e,'获取球员赛季表现'); } finally { this.loading=false } },
    async loadTransfers(playerId,{force=false}={}){ const now=Date.now(); const ts=this.lastTransfersFetched[playerId]; if(!force && ts && now-ts<TTL_TRANSFERS && this.transfersCache[playerId]) return {success:true,data:this.transfersCache[playerId],cached:true}; this.loading=true; this.error=null; try{ const r=await fetchPlayerTeamChanges(playerId); const d=r.data; if(d?.success===true || d?.status==='success'){ this.transfersCache[playerId]=d.data; this.lastTransfersFetched[playerId]=Date.now(); return {success:true,data:d.data}; } return {success:false,error:d?.message}; }catch(e){ return this._err(e,'获取球员转队历史'); } finally { this.loading=false } },
    async compare(playerIds, seasonIds=[]){ this.loading=true; this.error=null; try{ const r=await comparePlayersAcrossSeasons(playerIds,seasonIds); const d=r.data; if(d?.success===true || d?.status==='success'){ this.compareResult=d.data; return {success:true,data:d.data}; } return {success:false,error:d?.message}; }catch(e){ return this._err(e,'球员对比'); } finally { this.loading=false } }
  }
})
