/** usePlayerHistory (inlined) */
import { ref } from 'vue'
import { fetchPlayerAggregate } from '@/domain/player/playerService'
import logger from '@/utils/logger'
export function usePlayerHistory({ loader } = {}) {
	const player = ref(null); const stats = ref(null); const seasons = ref([]); const teamHistories = ref([]); const loading = ref(false); const error = ref(null)
	async function load(playerId,{force=false}={}){ if(!playerId){ error.value = new Error('缺少 playerId'); return } loading.value=true; error.value=null; try { const agg = await fetchPlayerAggregate(playerId,{ force, loader }); player.value=agg.player; stats.value=agg.stats; seasons.value=agg.seasons; teamHistories.value=agg.teamHistories } catch(e){ error.value=e; logger.error('[usePlayerHistory] 加载失败:', e) } finally { loading.value=false } }
	return { player, stats, seasons, teamHistories, loading, error, load }
}
