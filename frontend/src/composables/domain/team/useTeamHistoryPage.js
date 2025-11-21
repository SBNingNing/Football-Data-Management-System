/**
 * 球队历史页面组合函数
 * 管理球队历史页面的路由解析、数据加载和导航操作
 */
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import logger from '@/utils/logger'
import { useTeamHistoryStore } from '@/store/modules'
import { useTeamHistory } from './useTeamHistory.js'
import { normalizeError } from '@/utils/error'

/**
 * 球队历史页面组合函数
 * @returns {Object} 页面状态和操作方法
 */
export function useTeamHistoryPage() {
  // =========================
  // 路由和 Store
  // =========================
  
  const route = useRoute()
  const router = useRouter()
  const historyStore = useTeamHistoryStore()

  // =========================
  // 响应式状态
  // =========================
  
  // 当前活跃的赛季
  const activeSeason = ref(null)
  
  // 刷新状态
  const refreshing = ref(false)

  // =========================
  // 球队历史数据
  // =========================
  
  const { 
    team, 
    records, 
    loading, 
    error, 
    load 
  } = useTeamHistory({
    loader: (name, opts) => historyStore.loadComplete(name, opts)
  })

  /**
   * 初始化页面数据
   */
  async function init() {
    // 获取球队名称（支持多种路由参数格式）
    const teamName = route.params.teamName || route.query.teamName || route.query.name
    
    logger.debug('[team_history] teamName:', teamName)

    if (!teamName) {
      error.value = normalizeError(new Error('缺少球队名称'))
      return
    }

    // 加载球队数据
    await load(teamName)

    // 设置默认活跃赛季
    if (team.value?.records?.length) {
      activeSeason.value = team.value.records[0].id
    }
  }

  // =========================
  // 导航方法

  /**
   * 返回首页
   */
  function goToHomePage() {
    router.replace('/home')
  }

  /**
   * 跳转到球员历史页面
   * @param {string} playerId - 球员ID
   */
  function goToPlayerHistory(playerId) {
    if (playerId) {
      router.push({
        name: 'PlayerCareer',
        query: { playerId }
      })
    }
  }

  /**
   * 导航到球员详情
   * @param {Object} player - 球员对象
   */
  function navigateToPlayer(player) {
    // 支持多种球员ID字段名
    const playerId = player.id || player.studentId || player.playerId
    
    if (!playerId) {
      logger.error('球员ID不存在', player)
      return
    }
    
    goToPlayerHistory(playerId)
  }

  // =========================
  // 操作方法

  /**
   * 刷新球队数据
   * @param {boolean} force - 是否强制刷新
   */
  async function refreshTeamData(force = false) {
    const teamName = team.value?.teamName || route.params.teamName
    
    if (!teamName) return

    refreshing.value = true
    
    try {
      await load(teamName, { force })
    } finally {
      refreshing.value = false
    }
  }

  /**
   * 重试加载数据
   */
  function handleRetry() {
    init()
  }

  return {
    // 数据状态
    team,
    records,
    loading,
    error,
    activeSeason,
    refreshing,
    
    // 操作方法
    refreshTeamData,
    navigateToPlayer,
    goToHomePage,
    init,
    handleRetry
  }
}
