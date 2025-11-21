/**
 * useMatchDetailPage (inlined)
 * 页面编排：路由解析、玩家过滤+分页、事件回退推导玩家、状态文本/类名计算。
 */
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMatchDetail } from './useMatchDetail.js'
import { MATCH_EVENT_TYPES } from '@/constants/match'
import { normalizeError } from '@/utils/error'
import logger from '@/utils/logger'

export function useMatchDetailPage(){
	const route = useRoute(); const router = useRouter()
	const { match, players, events, loading, error, load } = useMatchDetail()
	// 状态管理
	const selectedTeam = ref('all')
	const currentPage = ref(1)
	const pageSize = ref(12)

	// 样式计算函数
	function getMatchStatusClass() {
		const status = match.value?.status
		
		if (status === 'F') return 'status-completed'
		if (status === 'O') return 'status-ongoing'
		if (status === 'P') return 'status-upcoming'
		
		return 'status-completed'
	}

	function getStatusTextForComponent() {
		if (!match.value) return '未知状态'  
		// 根据状态返回文本
		const status = match.value.status
		if (status === 'F') return '已结束'
		if (status === 'O') return '进行中'
		if (status === 'P') return '未开始'
		return '未知状态'
	}

	// 计算属性
	const filteredPlayers = computed(() => {
		return selectedTeam.value === 'all' 
			? players.value 
			: players.value.filter(p => p.teamName === selectedTeam.value)
	})

	const paginatedPlayers = computed(() => {
		const start = (currentPage.value - 1) * pageSize.value
		return filteredPlayers.value.slice(start, start + pageSize.value)
	})

	// 分页处理函数
	function handlePageSizeChange(size) {
		pageSize.value = size
		currentPage.value = 1
	}

	function handleCurrentPageChange(page) {
		currentPage.value = page
	}
	/**
	 * 从比赛事件中推导球员数据
	 * 当没有球员数据但有事件数据时，从事件中提取球员信息和统计
	 */
	function derivePlayersFromEvents() {
		// 如果已有球员数据或没有事件数据，则跳过
		if (players.value.length > 0 || events.value.length === 0) {
			return
		}

		const playerStats = new Map()

		// 遍历所有事件，统计球员数据
		events.value.forEach(event => {
			if (!event.player_id) return

			// 初始化球员统计数据
			if (!playerStats.has(event.player_id)) {
				playerStats.set(event.player_id, {
					playerId: event.player_id,
					playerName: event.player_name || '未知球员',
					teamName: event.team_name || '未知球队',
					playerNumber: event.player_number || 0,
					goals: 0,
					ownGoals: 0,
					yellowCards: 0,
					redCards: 0
				})
			}

			const playerStat = playerStats.get(event.player_id)

			// 根据事件类型更新统计
			switch (event.event_type) {
				case MATCH_EVENT_TYPES.GOAL:
					playerStat.goals++
					break
				case MATCH_EVENT_TYPES.OWN_GOAL:
					playerStat.ownGoals++
					break
				case MATCH_EVENT_TYPES.YELLOW:
					playerStat.yellowCards++
					break
				case MATCH_EVENT_TYPES.RED:
					playerStat.redCards++
					break
			}
		})

		// 更新球员数据
		players.value = Array.from(playerStats.values())
	}

	/**
	 * 初始化页面数据
	 */
	async function init() {
		// 获取比赛ID（支持多种路由参数格式）
		const matchId = route.params.matchId || route.query.matchId || route.params.id

		logger.info('[比赛详情] 初始化页面数据', { 
			routeParams: route.params, 
			routeQuery: route.query, 
			matchId 
		})

		if (!matchId) {
			logger.error('[比赛详情] 未指定比赛ID')
			error.value = normalizeError(new Error('未指定比赛ID'))
			goBack()
			return
		}

		// 加载比赛数据
		logger.info('[比赛详情] 开始加载比赛数据:', matchId)
		await load(matchId)
		logger.info('[比赛详情] 加载完成:', { 
			match: match.value, 
			players: players.value?.length, 
			events: events.value?.length,
			loading: loading.value,
			error: error.value
		})

		// 如果没有球员数据，尝试从事件中推导
		if (players.value.length === 0) {
			derivePlayersFromEvents()
		}
	}

	/**
	 * 查看球员历史记录
	 * @param {string} playerId - 球员ID
	 */
	function viewPlayerHistory(playerId) {
		if (playerId) {
			router.push({
				name: 'PlayerDetail',
				params: { playerId }
			})
		}
	}

	/**
	 * 返回上一页
	 */
	function goBack() {
		if (window.history.length > 1) {
			router.back()
		} else {
			router.push('/')
		}
	}

	/**
	 * 重试加载数据
	 */
	function retry() {
		init()
	}
	return {
		// 响应式数据
		match,
		players,
		events,
		loading,
		error,
		selectedTeam,
		currentPage,
		pageSize,
		
		// 计算属性
		filteredPlayers,
		paginatedPlayers,
		
		// 方法
		init,
		retry,
		viewPlayerHistory,
		handlePageSizeChange,
		handleCurrentPageChange,
		getMatchStatusClass,
		getMatchStatusText: getStatusTextForComponent,
		goBack
	}
}

export default useMatchDetailPage
