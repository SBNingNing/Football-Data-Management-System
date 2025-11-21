// useMatchStore: 比赛数据
import { defineStore } from 'pinia'
import { fetchMatches, createMatch, updateMatch, deleteMatch, completeMatch, getMatchDetail } from '@/api/matches'

export const useMatchStore = defineStore('matches', {
  state: () => ({ list: [], loading: false, error: null }),
  actions: {
  _err(e, op){ const msg = e?.message || op + '失败'; this.error = msg; return {success:false,error:msg,statusCode:e?.statusCode}},
    async loadAll(params = {}){ 
      this.loading=true; 
      this.error=null; 
      try{ 
        const response = await fetchMatches(params); 
        // 兼容处理：httpClient 可能返回 { ok:true, data: { status:'success', data:[...] } }
        // 或者直接返回 { ok:true, data: [...] } (如果 httpClient 自动解包)
        // 或者 response 本身就是数据 (如果 fetchMatches 内部处理了)
        
        let rawData = response.data || response;
        
        // 如果是 { status: 'success', data: [...] } 结构
        if (rawData && typeof rawData === 'object' && !Array.isArray(rawData) && Array.isArray(rawData.data)) {
          this.list = rawData.data;
        } else if (Array.isArray(rawData)) {
          this.list = rawData;
        } else {
          this.list = [];
        }
        
        return {success:true, data:this.list}; 
      }catch(e){ 
        return this._err(e,'获取比赛列表'); 
      } finally { 
        this.loading=false 
      } 
    },
    // 优化：仅刷新单场比赛数据，避免全量加载
    async refreshMatch(id) {
      if (!id) return { success: false, error: '缺少比赛ID' };
      try {
        const response = await getMatchDetail(id);
        const rawData = response.data || response;
        
        // 确保获取到的是比赛数据对象
        const matchData = (rawData && rawData.data) ? rawData.data : rawData;
        
        if (matchData && matchData.id) {
          // 查找并更新列表中的项
          const index = this.list.findIndex(m => m.id === id || m.matchId === id);
          if (index !== -1) {
            // 保持列表引用，仅更新内容，或者替换对象
            // 注意：getMatchDetail 返回的字段可能比列表多，也可能字段名略有不同（取决于后端实现）
            // 这里假设 getMatchDetail 返回的数据结构与列表项兼容，或者包含必要字段
            // 如果后端 getMatchDetail 返回的是详细结构，我们需要确保它包含列表所需的字段
            // 例如：home_score, away_score, status 等
            
            // 简单合并，优先使用新数据
            this.list[index] = { ...this.list[index], ...matchData };
            return { success: true, data: this.list[index] };
          }
        }
        return { success: false, error: '未找到比赛或数据无效' };
      } catch (e) {
        // 静默失败或记录日志，不影响整体流程
        console.error('刷新单场比赛失败', e);
        return { success: false, error: e.message };
      }
    },
    async create(payload){ this.loading=true; this.error=null; try{ const r=await createMatch(payload); if(r.data.success===true || r.data.status==='success'){ await this.loadAll(); return {success:true,data:r.data}; } return {success:false,error:r.data.message}; }catch(e){ return this._err(e,'创建比赛'); } finally { this.loading=false } },
    async update(id,payload){ this.loading=true; this.error=null; try{ const r=await updateMatch(id,payload); if(r.data.success===true || r.data.status==='success'){ await this.loadAll(); return {success:true,data:r.data}; } return {success:false,error:r.data.message}; }catch(e){ return this._err(e,'更新比赛'); } finally { this.loading=false } },
    async remove(id){ this.loading=true; this.error=null; try{ const r=await deleteMatch(id); if(r.data.success===true || r.data.status==='success'){ await this.loadAll(); return {success:true}; } return {success:false,error:r.data.message}; }catch(e){ return this._err(e,'删除比赛'); } finally { this.loading=false } },
    async complete(id){ this.loading=true; this.error=null; try{ const r=await completeMatch(id); if(r.data.success===true || r.data.status==='success'){ await this.loadAll(); return {success:true,data:r.data}; } return {success:false,error:r.data.message}; }catch(e){ return this._err(e,'完赛操作'); } finally { this.loading=false } }
  }
})
