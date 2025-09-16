// useCompetitionStore: 竞赛（大项）列表 / 详情 / CRUD + 统计摘取
import { defineStore } from 'pinia'
import { fetchCompetitions, fetchCompetitionById, createCompetition, updateCompetition, deleteCompetition } from '@/api/competitions'
import { DEFAULT_TTL_MS } from '@/store/config'

export const useCompetitionStore = defineStore('competitions', {
  state: () => ({ list: [], statistics: null, current: null, loading: false, error: null, lastFetched: 0 }),
  actions: {
    _err(e, op){ const msg = e?.message || op + '失败'; this.error = msg; return { success:false, error: msg, statusCode: e?.statusCode } },
  async loadAll({ force=false, params={} } = {}){ const TTL=DEFAULT_TTL_MS; const now=Date.now(); if(!force && this.lastFetched && (now-this.lastFetched)<TTL){ return { success:true, data:this.list, cached:true } }
      this.loading=true; this.error=null; try{ const r=await fetchCompetitions(params); const d=r.data; if(d?.success===true || d?.status==='success'){ const data=d.data; this.list = Array.isArray(data?.competitions)?data.competitions:[]; this.statistics = data?.statistics || null } else if(Array.isArray(d)){ this.list=d } this.lastFetched=Date.now(); return { success:true, data:this.list } }catch(e){ return this._err(e,'获取赛事大项列表') } finally { this.loading=false } },
    async loadOne(id){ this.loading=true; this.error=null; try{ const r=await fetchCompetitionById(id); const d=r.data; if(d?.success===true || d?.status==='success'){ this.current=d.data; return {success:true,data:d.data} } return {success:false,error:d?.message||'获取失败'} }catch(e){ return this._err(e,'获取赛事大项详情') } finally { this.loading=false } },
    async create(payload){ this.loading=true; this.error=null; try{ const r=await createCompetition(payload); if(r.data?.success===true || r.data?.status==='success'){ await this.loadAll({force:true}); return {success:true,data:r.data} } return {success:false,error:r.data?.message} }catch(e){ return this._err(e,'创建赛事大项') } finally { this.loading=false } },
    async update(id,payload){ this.loading=true; this.error=null; try{ const r=await updateCompetition(id,payload); if(r.data?.success===true || r.data?.status==='success'){ await this.loadAll({force:true}); return {success:true,data:r.data} } return {success:false,error:r.data?.message} }catch(e){ return this._err(e,'更新赛事大项') } finally { this.loading=false } },
    async remove(id){ this.loading=true; this.error=null; try{ const r=await deleteCompetition(id); if(r.data?.success===true || r.data?.status==='success'){ this.list = this.list.filter(c=>c.id!==id); return {success:true} } return {success:false,error:r.data?.message} }catch(e){ return this._err(e,'删除赛事大项') } finally { this.loading=false } }
  }
})
