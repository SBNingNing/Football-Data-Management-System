/**
 * 比赛类型元数据组合函数
 * 提供比赛类型相关的标签、样式和统计功能
 */
import { computed, unref } from 'vue'
import useCompetitions from '@/composables/admin/useCompetitions'

/**
 * 比赛类型元数据组合函数
 * @returns {Object} 比赛类型相关的工具函数
 */
export default function useMatchTypeMeta() {
  const { getCompetitionLabel: getDynamicLabel, competitions } = useCompetitions()

  /**
   * 获取比赛类型的中文标签
   * @param {string} type - 比赛类型
   * @returns {string} 中文标签
   */
  const getMatchTypeLabel = (type) => {
    return getDynamicLabel(type) || type || '未知'
  }

  /**
   * 获取比赛类型对应的标签样式
   * @param {string} type - 比赛类型
   * @returns {string} Element Plus 标签样式
   */
  const getMatchTypeTagType = (type) => {
    const label = getMatchTypeLabel(type) || ''
    if (label.includes('冠军')) return 'warning'
    if (label.includes('巾帼')) return 'danger'
    if (label.includes('八人')) return 'success'
    return 'info'
  }

  /**
   * 获取指定比赛类型的统计数据
   * @param {string} type - 比赛类型
   * @param {Object} sources - 数据源
   * @param {Array} sources.teams - 球队列表
   * @param {Array} sources.matches - 比赛列表
   * @param {Array} sources.events - 事件列表
   * @returns {Object} 统计结果
   */
  const getMatchTypeStats = (type, { teams = [], matches = [], events = [] } = {}) => {
    if (!type) {
      return {
        teams: 0,
        matches: 0,
        events: 0
      }
    }

    // 解析 type 对应的 ID 和 Name
    const compList = unref(competitions)
    const comp = compList.find(c => c.id == type || c.name === type)
    
    const typeId = comp ? comp.id : (typeof type === 'number' ? type : null)
    const typeName = comp ? comp.name : (typeof type === 'string' ? type : null)

    const filterFn = (item) => {
      if (!item) return false
      // 1. 优先匹配 competitionId (如果存在)
      if (item.competitionId && typeId && item.competitionId == typeId) return true
      
      // 2. 匹配 matchType 字符串 (如果存在)
      if (item.matchType && typeName && item.matchType === typeName) return true
      
      // 3. 兜底：直接比较
      if (item.matchType == type || item.type == type || item.competitionId == type) return true
      
      return false
    }

    return {
      teams: teams.filter(filterFn).length,
      matches: matches.filter(filterFn).length,
      events: events.filter(filterFn).length
    }
  }

  /**
   * 创建响应式统计数据
   * @param {import('vue').Ref} matchTypeRef - 比赛类型响应式引用
   * @param {Object} sources - 数据源
   * @returns {import('vue').ComputedRef} 响应式统计结果
   */
  const createReactiveStats = (matchTypeRef, sources) => {
    return computed(() => getMatchTypeStats(matchTypeRef.value, sources))
  }

  return {
    getMatchTypeLabel,
    getMatchTypeTagType,
    getMatchTypeStats,
    createReactiveStats
  }
}
