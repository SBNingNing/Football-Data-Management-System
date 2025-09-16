/**
 * useMatchRecords (inlined)
 * 提供统一的比赛记录分页加载与过滤状态
 */
import { ref, reactive } from 'vue'
import { fetchMatchRecords } from '@/domain/match/matchService'
import logger from '@/utils/logger'

export function useMatchRecords(initialQuery = {}) {
	const records = ref([])
	const total = ref(0)
	const loading = ref(false)
	const error = ref(null)
	const query = reactive({ type:'', status:'', keyword:'', page:1, pageSize:10, ...initialQuery })

	async function load(overrides = {}) {
		loading.value = true; error.value = null
		try {
			const token = localStorage.getItem('token') || sessionStorage.getItem('token')
			if (!token) { records.value = []; total.value = 0; return }
			const { ok, data, error: err } = await fetchMatchRecords({ token, params: { ...query, ...overrides } })
			if (!ok) { error.value = err; records.value = []; total.value = 0; return }
			records.value = data.records; total.value = data.total
		} catch (e) { error.value = e; logger.error('[useMatchRecords] 加载失败', e) }
		finally { loading.value = false }
	}
	// 返回 Promise 以便调用方可以 await，配合反馈统一 pending
	function setFilter(partial={}) { Object.assign(query, partial, { page:1 }); return load() }
	function setPage(page){ query.page = page; return load() }
	function reset(){ Object.assign(query, { type:'', status:'', keyword:'', page:1, pageSize:10 }); return load() }
	return { records, total, loading, error, query, load, setFilter, setPage, reset }
}

export default useMatchRecords
