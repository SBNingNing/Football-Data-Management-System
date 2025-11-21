/**
 * 球员统计相关逻辑组合函数
 * 提供轻量级球员统计查询功能
 */

const GOAL_TYPE_SET = new Set(['进球', 'goal'])

/**
 * @typedef {Object} PlayerStatsReturn
 * @property {(playerName:string)=>number} getPlayerGoals 获取指定球员进球次数
 * @property {(playerName:string, cardType:string)=>number} getPlayerCards 获取指定球员某类卡牌次数
 */

/**
 * 球员统计组合函数
 * @param {import('vue').Ref<Array>|{ value: Array }} eventsRef 事件数组引用
 * @returns {PlayerStatsReturn}
 */
export default function usePlayerStats(eventsRef) {
  /**
   * 获取指定球员的进球次数
   * @param {string} playerName 球员姓名
   * @returns {number} 进球次数
   */
  const getPlayerGoals = (playerName) => {
    try {
      const list = eventsRef?.value
      
      if (!playerName || !Array.isArray(list)) {
        return 0
      }
      
      return list.filter(event => {
        if (!event) return false
        
        const isTargetPlayer = event.playerName === playerName || event.player === playerName
        const isGoalEvent = GOAL_TYPE_SET.has(event.eventType) || GOAL_TYPE_SET.has(event.type)
        
        return isTargetPlayer && isGoalEvent
      }).length
    } catch {
      return 0
    }
  }

  /**
   * 获取指定球员的卡牌次数
   * @param {string} playerName 球员姓名
   * @param {string} cardType 卡牌类型 ('黄牌' | 'yellow_card' | '红牌' | 'red_card')
   * @returns {number} 卡牌次数
   */
  const getPlayerCards = (playerName, cardType) => {
    try {
      const list = eventsRef?.value
      
      if (!playerName || !cardType || !Array.isArray(list)) {
        return 0
      }
      
      return list.filter(event => {
        if (!event) return false
        
        const isTargetPlayer = event.playerName === playerName || event.player === playerName
        const isTargetCard = event.eventType === cardType || event.type === cardType
        
        return isTargetPlayer && isTargetCard
      }).length
    } catch {
      return 0
    }
  }

  return {
    getPlayerGoals,
    getPlayerCards
  }
}
