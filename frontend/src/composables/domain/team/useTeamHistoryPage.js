/** useTeamHistoryPage (inlined) */
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import logger from '@/utils/logger'
import { useTeamHistoryStore } from '@/store/modules'
import { useTeamHistory } from './useTeamHistory.js'
import { normalizeError } from '@/utils/error'

export function useTeamHistoryPage(){
	const route = useRoute(); const router = useRouter(); const activeSeason = ref(null); const refreshing = ref(false)
	const historyStore = useTeamHistoryStore()
	const { team, records, loading, error, load } = useTeamHistory({ loader: (name, opts)=> historyStore.loadComplete(name, opts) })
	async function init(){ const teamName = route.params.teamName || route.query.teamName || route.query.name; logger.debug('[team_history] teamName:', teamName); if(!teamName){ error.value = normalizeError(new Error('缺少球队名称')); return } await load(teamName); if(team.value?.records?.length){ activeSeason.value = team.value.records[0].id } }
	function goToHomePage(){ router.replace('/home') }
	function goToPlayerHistory(playerId){ if(playerId) router.push({ name:'PlayerCareer', query:{ playerId } }) }
	function navigateToPlayer(player){ const playerId = player.id || player.studentId || player.playerId; if(!playerId){ logger.error('球员ID不存在', player); return } goToPlayerHistory(playerId) }
	async function refreshTeamData(force=false){ const name = team.value?.teamName || route.params.teamName; if(!name) return; refreshing.value=true; await load(name,{ force }); refreshing.value=false }
	function handleRetry(){ init() }
	return { team, records, loading, error, activeSeason, refreshing, refreshTeamData, navigateToPlayer, goToHomePage, init, handleRetry }
}
