/** usePlayerHistoryPage (inlined) */
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { normalizeError } from '@/utils/error'
import { usePlayerHistoryStore } from '@/store/modules'
import { usePlayerHistory } from './usePlayerHistory.js'
import logger from '@/utils/logger'

export function usePlayerHistoryPage(){
	const route = useRoute(); const router = useRouter(); const activeSeason = ref(null); const refreshing = ref(false)
	const historyStore = usePlayerHistoryStore()
	const { player, stats, seasons, teamHistories, loading, error, load } = usePlayerHistory({ loader: (playerId)=> historyStore.loadComplete(playerId,{}) })
	async function init(){ const playerId = route.params.playerId || route.query.playerId; logger.debug('[player_history] route playerId:', playerId); if(!playerId){ error.value = normalizeError(new Error('缺少 playerId')); return } await load(playerId); if(player.value?.seasons?.length){ activeSeason.value = player.value.seasons[0].season_name } }
	async function refreshPlayer(force=false){ const id = player.value?.id || route.params.playerId; if(!id) return; refreshing.value=true; await load(id,{ force }); refreshing.value=false }
	function retry(){ init() }
	function goToHomePage(){ router.push('/') }
	return { player, stats, seasons, teamHistories, loading, error, activeSeason, refreshing, init, refreshPlayer, retry, goToHomePage }
}
