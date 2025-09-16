/**
 * useMatchDetail (inlined)
 * 职责: 为比赛详情视图提供响应式状态与加载方法
 */
import { ref } from 'vue'
import { fetchMatchAggregate } from '@/domain/match/matchService'
import logger from '@/utils/logger'

export function useMatchDetail() {
	const match = ref(null)
	const players = ref([])
	const events = ref([])
	const loading = ref(false)
	const error = ref(null)

	async function load(matchId, { force: _force = false } = {}) {
		if (!matchId) { error.value = new Error('缺少 matchId'); return }
		loading.value = true; error.value = null
		try {
			const res = await fetchMatchAggregate(matchId)
			if (res.ok) {
				match.value = res.data.match
				players.value = res.data.players
				events.value = res.data.events
			} else {
				error.value = res.error; logger.error('[useMatchDetail] 加载失败:', res.error)
			}
		} catch (err) {
			error.value = err; logger.error('[useMatchDetail] 加载失败(异常):', err)
		} finally { loading.value = false }
	}

	return { match, players, events, loading, error, load }
}

export default useMatchDetail
