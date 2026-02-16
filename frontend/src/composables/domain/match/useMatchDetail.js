/**
 * 比赛详情组合函数
 * 职责: 为比赛详情视图提供响应式状态与加载方法
 */
import { ref } from 'vue'
import { getMatchDetail } from '@/api/matches'
import logger from '@/utils/logger'

/**
 * 比赛详情组合函数
 * 提供比赛基本信息、球员数据、比赛事件的加载和管理
 * 
 * @returns {Object} 包含比赛详情相关的响应式数据和方法
 */
export function useMatchDetail() {
  // =========================
  // 响应式状态定义
  // =========================
  
  // 比赛基本信息
  const match = ref(null)
  
  // 参与比赛的球员列表
  const players = ref([])
  
  // 比赛事件列表（进球、黄牌、红牌等）
  const events = ref([])
  
  // 加载状态
  const loading = ref(false)
  
  // 错误信息
  const error = ref(null)

  // =========================
  // 数据加载方法
  // =========================

  /**
   * 加载比赛详情数据
   * @param {string} matchId - 比赛ID
   * @param {Object} options - 加载选项
   * @param {boolean} options.force - 是否强制刷新（预留参数）
   */
  async function load(matchId, { force: _force = false } = {}) {
    // 参数验证
    if (!matchId) {
      error.value = new Error('缺少 matchId')
      return
    }

    logger.info('[useMatchDetail] 开始加载比赛数据:', matchId)

    // 设置加载状态
    loading.value = true
    error.value = null

    try {
      // 获取比赛聚合数据
      logger.info('[useMatchDetail] 调用 getMatchDetail')
      const res = await getMatchDetail(matchId)
      logger.info('[useMatchDetail] getMatchDetail 响应:', res)
      
      if (res.ok) {
        // 成功时更新各项数据
        match.value = res.data
        players.value = res.data?.players || []
        events.value = res.data?.events || []
        
        logger.info('[useMatchDetail] 数据加载成功:', {
          match: match.value,
          playersCount: players.value?.length,
          eventsCount: events.value?.length
        })
      } else {
        // 处理业务错误
        error.value = res.error
        logger.error('[useMatchDetail] 加载失败:', res.error)
      }
    } catch (err) {
      // 处理网络或其他异常
      error.value = err
      logger.error('[useMatchDetail] 加载失败(异常):', err)
    } finally {
      // 清除加载状态
      loading.value = false
      logger.info('[useMatchDetail] 加载完成，loading状态已清除')
    }
  }

  // =========================
  // 返回值
  // =========================

  return {
    // 响应式数据
    match,
    players,
    events,
    loading,
    error,
    
    // 方法
    load
  }
}

export default useMatchDetail
