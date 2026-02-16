/**
 * 元数据管理组合函数
 * 管理赛季与赛事元数据的加载、刷新与快速实例反馈
 */
import { ref } from 'vue'
import { fetchSeasons } from '@/api/seasons'
import { fetchCompetitions } from '@/api/competitions'
import notify from '@/utils/notify'

/**
 * 元数据管理组合函数
 * @returns {Object} 元数据管理相关状态和方法
 */
export function useMetaData() {
  // 响应式数据
  const seasons = ref([])
  const competitions = ref([])
  const loadingMeta = ref(false)

  /**
   * 重新加载赛季数据
   */
  async function reloadSeasons() {
    const { ok, data, error } = await fetchSeasons()
    
    if (ok) {
      const rawList = data?.data || data || []
      seasons.value = rawList
    } else {
      notify.error(error?.message || '获取赛季失败')
    }
  }

  /**
   * 重新加载赛事数据
   */
  async function reloadCompetitions() {
    const { ok, data, error } = await fetchCompetitions()
    
    if (ok) {
      const rawData = data?.data || data || {}
      const list = rawData.competitions || []
      competitions.value = list
    } else {
      notify.error(error?.message || '获取赛事失败')
    }
  }

  /**
   * 重新加载所有元数据
   */
  async function reloadAll() {
    loadingMeta.value = true
    
    try {
      await Promise.all([
        reloadSeasons(),
        reloadCompetitions()
      ])
    } finally {
      loadingMeta.value = false
    }
  }

  /**
   * 处理销比赛快速操作
   */
  function handleTournamentQuick() {
    reloadAll()
  }

  return {
    // 响应式数据
    seasons,
    competitions,
    loadingMeta,
    
    // 方法
    reloadSeasons,
    reloadCompetitions,
    reloadAll,
    handleTournamentQuick
  }
}

export default useMetaData
