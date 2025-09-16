/** useTournamentHistory (inlined) */
import { ref } from 'vue'
import { fetchTournamentAggregate } from '@/domain/tournament/tournamentService'
import logger from '@/utils/logger'
import { normalizeError } from '@/utils/error'
export function useTournamentHistory(){
	const competition=ref(null); const topScorers=ref([]); const topCards=ref([]); const loading=ref(false); const error=ref(null); const lastLoadedName=ref(null); const retryCount=ref(0)
	async function load(name,{silent=false}={}){ if(!name){ error.value = normalizeError(new Error('缺少赛事名称')); return } if(!silent) loading.value=true; error.value=null; lastLoadedName.value=name; const { ok, data, error:svcError } = await fetchTournamentAggregate(name); if(ok){ competition.value=data.competition; topScorers.value=data.topScorers; topCards.value=data.topCards; retryCount.value=0 } else { error.value=normalizeError(svcError); logger.error('[useTournamentHistory] 加载失败:', svcError) } if(!silent) loading.value=false }
	async function retry(){ if(!lastLoadedName.value) return; retryCount.value += 1; return load(lastLoadedName.value) }
	return { competition, topScorers, topCards, loading, error, load, retry, retryCount }
}
