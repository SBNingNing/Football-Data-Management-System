/** useTeamHistory (inlined) */
import { ref } from 'vue'
import { fetchTeamAggregate } from '@/domain/team/teamService'
import logger from '@/utils/logger'
export function useTeamHistory({ loader } = {}) {
	const team = ref(null); const records = ref([]); const loading = ref(false); const error = ref(null)
	async function load(teamName,{force=false}={}){ if(!teamName){ error.value=new Error('缺少 teamName'); return } loading.value=true; error.value=null; try { const agg = await fetchTeamAggregate(teamName,{ force, loader }); team.value = agg.team; records.value = agg.records } catch(e){ error.value=e; logger.error('[useTeamHistory] 加载失败:', e) } finally { loading.value=false } }
	return { team, records, loading, error, load }
}
