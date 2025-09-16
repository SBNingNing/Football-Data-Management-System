/**
 * useMatchDetailPage (inlined)
 * 页面编排：路由解析、玩家过滤+分页、事件回退推导玩家、状态文本/类名计算。
 */
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMatchDetail } from './useMatchDetail.js'
import { getMatchStatusText, MATCH_EVENT_TYPES } from '@/constants/match'
import { normalizeError } from '@/utils/error'

export function useMatchDetailPage(){
	const route = useRoute(); const router = useRouter()
	const { match, players, events, loading, error, load } = useMatchDetail()
	const selectedTeam = ref('all'); const currentPage = ref(1); const pageSize = ref(12)
	function getMatchStatusClass(){ const s = match.value?.status; if (s==='completed') return 'status-completed'; if (s==='ongoing') return 'status-ongoing'; if (s==='pending'||s==='upcoming') return 'status-upcoming'; return 'status-completed' }
	function getMatchStatusTextComputed(){ return getMatchStatusText(match.value?.status) }
	const filteredPlayers = computed(()=> selectedTeam.value==='all' ? players.value : players.value.filter(p=>p.teamName===selectedTeam.value))
	const paginatedPlayers = computed(()=> { const start = (currentPage.value-1)*pageSize.value; return filteredPlayers.value.slice(start, start+pageSize.value) })
	function handlePageSizeChange(size){ pageSize.value = size; currentPage.value = 1 }
	function handleCurrentPageChange(p){ currentPage.value = p }
	function derivePlayersFromEvents(){ if (players.value.length>0 || events.value.length===0) return; const stats=new Map(); events.value.forEach(ev=>{ if(!ev.player_id) return; if(!stats.has(ev.player_id)){ stats.set(ev.player_id,{ playerId:ev.player_id, playerName:ev.player_name||'未知球员', teamName:ev.team_name||'未知球队', playerNumber:ev.player_number||0, goals:0, ownGoals:0, yellowCards:0, redCards:0 }) } const p=stats.get(ev.player_id); switch(ev.event_type){ case MATCH_EVENT_TYPES.GOAL: p.goals++; break; case MATCH_EVENT_TYPES.OWN_GOAL: p.ownGoals++; break; case MATCH_EVENT_TYPES.YELLOW: p.yellowCards++; break; case MATCH_EVENT_TYPES.RED: p.redCards++; break } }); players.value = Array.from(stats.values()) }
	async function init(){ const matchId = route.params.matchId || route.query.matchId || route.params.id; if(!matchId){ error.value = normalizeError(new Error('未指定比赛ID')); goBack(); return } await load(matchId); if (players.value.length===0) derivePlayersFromEvents() }
	function viewPlayerHistory(playerId){ if(playerId) router.push({ name:'PlayerDetail', params:{ playerId } }) }
	function goBack(){ if (window.history.length>1) router.back(); else router.push('/') }
	function retry(){ init() }
	return { match, players, events, loading, error, selectedTeam, currentPage, pageSize, filteredPlayers, paginatedPlayers, init, retry, viewPlayerHistory, handlePageSizeChange, handleCurrentPageChange, getMatchStatusClass, getMatchStatusText: getMatchStatusTextComputed, goBack }
}

export default useMatchDetailPage
