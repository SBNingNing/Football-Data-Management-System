// 球员统计相关逻辑抽离
// 仅提供轻量查询函数；若后续需要聚合排行榜，可扩展 aggregate 函数或 computed 排行。

const GOAL_TYPE_SET = new Set(['进球', 'goal'])

/**
 * @typedef {Object} PlayerStatsReturn
 * @property {(playerName:string)=>number} getPlayerGoals 获取指定球员进球次数
 * @property {(playerName:string, cardType:string)=>number} getPlayerCards 获取指定球员某类卡牌次数（'黄牌' | 'yellow_card' | '红牌' | 'red_card' 等）
 */

/**
 * @param {import('vue').Ref<Array>|{ value: Array }} eventsRef 事件数组 Ref（元素可含 playerName / player, eventType / type）
 * @returns {PlayerStatsReturn}
 */
export default function usePlayerStats(eventsRef) {
  /** @type {(playerName:string)=>number} */
  const getPlayerGoals = (playerName) => {
    try {
      const list = eventsRef?.value
      if (!playerName || !Array.isArray(list)) return 0
      return list.filter(e => e && (e.playerName === playerName || e.player === playerName) &&
        (GOAL_TYPE_SET.has(e.eventType) || GOAL_TYPE_SET.has(e.type))).length
    } catch { return 0 }
  }

  /** @type {(playerName:string, cardType:string)=>number} */
  const getPlayerCards = (playerName, cardType) => {
    try {
      const list = eventsRef?.value
      if (!playerName || !cardType || !Array.isArray(list)) return 0
      return list.filter(e => e && (e.playerName === playerName || e.player === playerName) &&
        (e.eventType === cardType || e.type === cardType)).length
    } catch { return 0 }
  }

  return { getPlayerGoals, getPlayerCards }
}
