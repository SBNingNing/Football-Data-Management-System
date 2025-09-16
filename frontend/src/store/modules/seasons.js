// useSeasonStore: 赛季列表 / 详情 / CRUD
import { defineStore } from 'pinia'
import { fetchSeasons, fetchSeasonById, createSeason, updateSeason, deleteSeason } from '@/api/seasons'
import { DEFAULT_TTL_MS } from '@/store/config'

export const useSeasonStore = defineStore('seasons', {
  state: () => ({ list: [], current: null, loading: false, error: null, lastFetched: 0 }),
  actions: {
    _err(e, op){ const msg = e?.message || op + '失败'; this.error = msg; return { success:false, error: msg, statusCode: e?.statusCode } },
  async loadAll({ force=false } = {}){ const TTL=DEFAULT_TTL_MS; const now=Date.now(); if(!force && this.lastFetched && (now-this.lastFetched)<TTL){ return { success:true, data:this.list, cached:true } }
      this.loading=true; this.error=null; try{ const r=await fetchSeasons(); const d=r.data; if(d?.success===true || d?.status==='success'){ this.list = Array.isArray(d.data)?d.data:[] } else if(Array.isArray(d)){ this.list=d } this.lastFetched=Date.now(); return { success:true, data:this.list } }catch(e){ return this._err(e,'获取赛季列表') } finally { this.loading=false } },
    async loadOne(id){ this.loading=true; this.error=null; try{ const r=await fetchSeasonById(id); const d=r.data; if(d?.success===true || d?.status==='success'){ this.current=d.data; return {success:true,data:d.data} } return {success:false,error:d?.message||'获取失败'} }catch(e){ return this._err(e,'获取赛季详情') } finally { this.loading=false } },
    async create(payload){ this.loading=true; this.error=null; try{ const r=await createSeason(payload); if(r.data?.success===true || r.data?.status==='success'){ await this.loadAll({force:true}); return {success:true,data:r.data} } return {success:false,error:r.data?.message} }catch(e){ return this._err(e,'创建赛季') } finally { this.loading=false } },
    async update(id,payload){ this.loading=true; this.error=null; try{ const r=await updateSeason(id,payload); if(r.data?.success===true || r.data?.status==='success'){ await this.loadAll({force:true}); return {success:true,data:r.data} } return {success:false,error:r.data?.message} }catch(e){ return this._err(e,'更新赛季') } finally { this.loading=false } },
    async remove(id){ this.loading=true; this.error=null; try{ const r=await deleteSeason(id); if(r.data?.success===true || r.data?.status==='success'){ this.list = this.list.filter(s=>s.id!==id); return {success:true} } return {success:false,error:r.data?.message} }catch(e){ return this._err(e,'删除赛季') } finally { this.loading=false } }
  }
})
