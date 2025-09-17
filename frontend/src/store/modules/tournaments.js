// useTournamentStore: 赛事数据（列表 / 当前 / 快速创建 / 赛事实例）
import { defineStore } from 'pinia'
import { 
  fetchTournaments,
  fetchTournamentByNameOrId,
  createTournament,
  updateTournament,
  deleteTournament,
  createTournamentInstance,
  updateTournamentInstance,
  quickCreateTournament
} from '@/api/tournaments'

export const useTournamentStore = defineStore('tournaments', {
  state: () => ({
    list: [],
    current: null,
    loading: false,
    error: null,
    lastQuickResult: null
  }),
  actions: {
    _err(e, op){ const msg = e?.message || op + '失败'; this.error = msg; return {success:false,error:msg,statusCode:e?.statusCode} },
    async loadAll(params){ this.loading=true; this.error=null; try{ const r=await fetchTournaments(params); const d=r.data; // 后端统一格式化 wrapper
      // 兼容旧字段 status & 新字段 success
      if(d?.success===true || d?.status==='success'){ const rec = d.data?.records || d.data?.tournaments || d.data; this.list = Array.isArray(rec)?rec:[]; } else if(Array.isArray(d)){ this.list = d; }
      return {success:true,data:this.list}; }catch(e){ return this._err(e,'获取赛事列表'); } finally { this.loading=false } },
    async loadOne(nameOrId){ this.loading=true; this.error=null; try{ const r=await fetchTournamentByNameOrId(nameOrId); const d=r.data; if(d?.success===true || d?.status==='success'){ this.current = d.data; return {success:true,data:d.data}; } return {success:false,error:d?.message||'获取失败'} }catch(e){ return this._err(e,'获取赛事详情'); } finally { this.loading=false } },
  async create(payload){ this.loading=true; this.error=null; try{ const r=await createTournament(payload); if(r.data?.success===true || r.data?.status==='success'){ await this.loadAll(); return {success:true,data:r.data}; } return {success:false,error:r.data?.message}; }catch(e){ return this._err(e,'创建赛事实例'); } finally { this.loading=false } },
    async update(id,payload){ this.loading=true; this.error=null; try{ const r=await updateTournament(id,payload); if(r.data?.success===true || r.data?.status==='success'){ await this.loadAll(); return {success:true,data:r.data}; } return {success:false,error:r.data?.message}; }catch(e){ return this._err(e,'更新赛事'); } finally { this.loading=false } },
    async remove(id){ this.loading=true; this.error=null; try{ const r=await deleteTournament(id); if(r.data?.success===true || r.data?.status==='success'){ await this.loadAll(); return {success:true}; } return {success:false,error:r.data?.message}; }catch(e){ return this._err(e,'删除赛事'); } finally { this.loading=false } },
    async createInstance(payload){ this.loading=true; this.error=null; try{ const r=await createTournamentInstance(payload); if(r.data?.success===true || r.data?.status==='success'){ await this.loadAll(); return {success:true,data:r.data}; } return {success:false,error:r.data?.message}; }catch(e){ return this._err(e,'创建赛事实例'); } finally { this.loading=false } },
    async updateInstance(id,payload){ this.loading=true; this.error=null; try{ const r=await updateTournamentInstance(id,payload); if(r.data?.success===true || r.data?.status==='success'){ await this.loadAll(); return {success:true,data:r.data}; } return {success:false,error:r.data?.message}; }catch(e){ return this._err(e,'更新赛事实例'); } finally { this.loading=false } },
    async quick(payload){ this.loading=true; this.error=null; try{ const r=await quickCreateTournament(payload); if(r.data?.success===true || r.data?.status==='success'){ this.lastQuickResult = r.data?.data; if(!payload?.dryRun){ await this.loadAll(); } return {success:true,data:r.data}; } return {success:false,error:r.data?.message}; }catch(e){ return this._err(e,'快速创建赛事'); } finally { this.loading=false } }
  }
})
