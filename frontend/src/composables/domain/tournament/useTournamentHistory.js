/**
 * 锦标赛历史组合函数
 * 提供锦标赛数据、射手榜、卡牌榜和所有比赛的加载和管理
 */
import { ref } from 'vue'
import { fetchTournamentAggregate } from '@/domain/tournament/tournamentService'
import logger from '@/utils/logger'
import { normalizeError } from '@/utils/error'

/**
 * 锦标赛历史组合函数
 * @returns {Object} 锦标赛历史相关的响应式数据和方法
 */
export function useTournamentHistory() {
  // =========================
  // 响应式状态定义
  // =========================
  
  // 比赛/锦标赛基本信息
  const competition = ref(null)
  
  // 射手榜数据
  const topScorers = ref([])
  
  // 卡牌榜数据
  const topCards = ref([])
  
  // 所有比赛列表
  const allMatches = ref([])
  
  // 加载状态
  const loading = ref(false)
  
  // 错误信息
  const error = ref(null)
  
  // 最后加载的赛事名称（用于重试）
  const lastLoadedName = ref(null)
  
  // 重试次数
  const retryCount = ref(0)

  /**
   * 加载锦标赛历史数据
   * @param {string} name - 赛事名称
   * @param {Object} options - 加载选项
   * @param {boolean} options.silent - 是否静默加载（不显示加载状态）
   */
  async function load(name, { silent = false } = {}) {
    // 参数验证
    if (!name) {
      error.value = normalizeError(new Error('缺少赛事名称'))
      return
    }

    // 设置加载状态
    if (!silent) {
      loading.value = true
    }
    
    error.value = null
    lastLoadedName.value = name

    try {
      // 调用服务获取数据
      const { ok, data, error: serviceError } = await fetchTournamentAggregate(name)

      if (ok) {
        // 成功时更新所有数据
        competition.value = data.competition
        topScorers.value = data.topScorers
        topCards.value = data.topCards
        allMatches.value = data.allMatches || []
        
        // 重置重试计数
        retryCount.value = 0
      } else {
        // 处理业务错误
        error.value = normalizeError(serviceError)
        logger.error('[useTournamentHistory] 加载失败:', serviceError)
      }
    } catch (e) {
      // 处理网络或其他异常
      error.value = normalizeError(e)
      logger.error('[useTournamentHistory] 加载异常:', e)
    } finally {
      // 清除加载状态
      if (!silent) {
        loading.value = false
      }
    }
  }

  /**
   * 重试加载数据
   * 使用最后一次加载的赛事名称重新加载
   */
  async function retry() {
    if (!lastLoadedName.value) {
      return
    }

    retryCount.value += 1
    return load(lastLoadedName.value)
  }

  return {
    // 响应式数据
    competition,
    topScorers,
    topCards,
    allMatches,
    loading,
    error,
    retryCount,
    
    // 方法
    load,
    retry
  }
}
