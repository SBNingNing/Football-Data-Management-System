/**
 * 球员历史页面组合函数
 * 管理球员历史页面的路由解析、数据加载和状态管理
 */
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { normalizeError } from '@/utils/error'
import { usePlayerHistoryStore } from '@/store/modules'
import { usePlayerHistory } from './usePlayerHistory.js'
import logger from '@/utils/logger'

/**
 * 球员历史页面组合函数
 * @returns {Object} 页面状态和操作方法
 */
export function usePlayerHistoryPage() {
  // =========================
  // 路由和 Store
  // =========================
  
  const route = useRoute()
  const router = useRouter()
  const historyStore = usePlayerHistoryStore()

  // 当前活跃的赛季
  const activeSeason = ref(null)
  
  // 刷新状态
  const refreshing = ref(false)

  // 球员历史数据
  const { 
    player, 
    stats, 
    seasons, 
    teamHistories, 
    loading, 
    error, 
    load 
  } = usePlayerHistory()

  /**
   * 初始化页面数据
   */
  async function init() {
    // 获取球员ID（支持多种路由参数格式）
    const playerId = route.params.playerId || route.query.playerId
    
    logger.debug('[player_history] route playerId:', playerId)

    if (!playerId) {
      error.value = normalizeError(new Error('缺少 playerId'))
      return
    }

    // 加载球员数据
    await load(playerId)

    // 设置默认活跃赛季
    if (player.value?.seasons?.length) {
      activeSeason.value = player.value.seasons[0].season_name
    }
  }
  /**
   * 刷新球员数据
   * @param {boolean} force - 是否强制刷新
   */
  async function refreshPlayer(force = false) {
    const playerId = player.value?.id || route.params.playerId
    
    if (!playerId) return

    refreshing.value = true
    
    try {
      await load(playerId, { force })
    } finally {
      refreshing.value = false
    }
  }

  /**
   * 重试加载数据
   */
  function retry() {
    init()
  }

  /**
   * 返回首页
   */
  function goToHomePage() {
    router.push('/home')
  }

  return {
    // 数据状态
    player,
    stats,
    seasons,
    teamHistories,
    loading,
    error,
    activeSeason,
    refreshing,
    
    // 操作方法
    init,
    refreshPlayer,
    retry,
    goToHomePage
  }
}
