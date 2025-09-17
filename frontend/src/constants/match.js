/**
 * constants/match.js
 * ---------------------------------------------
 * 比赛领域相关的常量/映射统一出口
 * 后续组件与服务都应引用这里，避免重复魔法字符串
 */

// 比赛状态（内部统一枚举）- 与后端数据库保持一致
export const MATCH_STATUS = Object.freeze({
  PENDING: 'P', // 未开始
  COMPLETED: 'F' // 已完赛
})

// 状态 -> 展示文本
export const MATCH_STATUS_TEXT = Object.freeze({
  [MATCH_STATUS.PENDING]: '未开始',
  [MATCH_STATUS.COMPLETED]: '已完赛'
})

// 状态 -> 标签 type (Element Plus)
export const MATCH_STATUS_TAG_TYPE = Object.freeze({
  [MATCH_STATUS.PENDING]: 'info',
  [MATCH_STATUS.COMPLETED]: 'success'
})

// 事件类型（根据后端/现有中文语义，可继续扩展）
export const MATCH_EVENT_TYPES = Object.freeze({
  GOAL: '进球',
  OWN_GOAL: '乌龙球',
  YELLOW: '黄牌',
  RED: '红牌',
  SUBSTITUTION: '换人',
  PENALTY: '点球'
})

// 事件 -> 样式 class 前缀（配合 match_detail.vue 的样式）
export const MATCH_EVENT_CLASS = Object.freeze({
  [MATCH_EVENT_TYPES.GOAL]: 'event-goal',
  [MATCH_EVENT_TYPES.OWN_GOAL]: 'event-own-goal',
  [MATCH_EVENT_TYPES.YELLOW]: 'event-yellow-card',
  [MATCH_EVENT_TYPES.RED]: 'event-red-card',
  [MATCH_EVENT_TYPES.SUBSTITUTION]: 'event-substitution',
  [MATCH_EVENT_TYPES.PENALTY]: 'event-penalty'
})

// 获取状态展示文本
export function getMatchStatusText(status){
  return MATCH_STATUS_TEXT[status] || '未开始'
}

// 获取标签类型
export function getMatchStatusTagType(status){
  return MATCH_STATUS_TAG_TYPE[status] || 'info'
}

// 事件类型 -> class（降级兼容传入中文）
export function getMatchEventClass(eventType){
  return MATCH_EVENT_CLASS[eventType] || MATCH_EVENT_CLASS[MATCH_EVENT_TYPES.GOAL] || ''
}