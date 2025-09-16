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
    _err(e, op){ const msg=e?.message||op+'失败'; this.error=msg; return {success:false,error:msg,statusCode:e?.statusCode} },
    async loadComplete(teamBaseId,{force=false}={}){ const now=Date.now(); const ts=this.lastCompleteFetched[teamBaseId]; if(!force && ts && now-ts<TTL_COMPLETE && this.completeCache[teamBaseId]) return {success:true,data:this.completeCache[teamBaseId],cached:true}; this.loading=true; this.error=null; try{ const r=await fetchTeamCompleteHistory(teamBaseId); const d=r.data; if(d?.success===true || d?.status==='success'){ this.completeCache[teamBaseId]=d.data; this.lastCompleteFetched[teamBaseId]=Date.now(); return {success:true,data:d.data}; } return {success:false,error:d?.message}; }catch(e){ return this._err(e,'获取球队完整历史'); } finally { this.loading=false } },
    async loadSeasonPerformance(teamBaseId,seasonId,{force=false}={}){ const now=Date.now(); if(!this.lastSeasonFetched[teamBaseId]) this.lastSeasonFetched[teamBaseId]={}; if(!this.seasonPerfCache[teamBaseId]) this.seasonPerfCache[teamBaseId]={}; const ts=this.lastSeasonFetched[teamBaseId][seasonId]; const cachedData=this.seasonPerfCache[teamBaseId][seasonId]; if(!force && ts && now-ts<TTL_SEASON && cachedData) return {success:true,data:cachedData,cached:true}; this.loading=true; this.error=null; try{ const r=await fetchTeamSeasonPerformance(teamBaseId,seasonId); const d=r.data; if(d?.success===true || d?.status==='success'){ this.seasonPerfCache[teamBaseId][seasonId]=d.data; this.lastSeasonFetched[teamBaseId][seasonId]=Date.now(); return {success:true,data:d.data}; } return {success:false,error:d?.message}; }catch(e){ return this._err(e,'获取球队赛季表现'); } finally { this.loading=false } },
    async loadTournamentHistory(teamBaseId,{force=false}={}){ const now=Date.now(); const ts=this.lastTournamentHistFetched[teamBaseId]; if(!force && ts && now-ts<TTL_TOURNAMENT && this.tournamentHistCache[teamBaseId]) return {success:true,data:this.tournamentHistCache[teamBaseId],cached:true}; this.loading=true; this.error=null; try{ const r=await fetchTeamTournamentHistory(teamBaseId); const d=r.data; if(d?.success===true || d?.status==='success'){ this.tournamentHistCache[teamBaseId]=d.data; this.lastTournamentHistFetched[teamBaseId]=Date.now(); return {success:true,data:d.data}; } return {success:false,error:d?.message}; }catch(e){ return this._err(e,'获取球队参赛历史'); } finally { this.loading=false } },
    async compare(teamBaseIds, seasonIds=[]){ this.loading=true; this.error=null; try{ const r=await compareTeamsAcrossSeasons(teamBaseIds,seasonIds); const d=r.data; if(d?.success===true || d?.status==='success'){ this.compareResult=d.data; return {success:true,data:d.data}; } return {success:false,error:d?.message}; }catch(e){ return this._err(e,'球队对比'); } finally { this.loading=false } }
  }
})
