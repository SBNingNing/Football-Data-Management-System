/**
 * 全局常量定义
 * 包含比赛状态、事件类型、比赛类型等
 */

// =====================================================================
// 比赛状态 (Match Status)
// =====================================================================

// 比赛状态（内部统一枚举）- 与后端数据库保持一致
export const MATCH_STATUS = Object.freeze({
  PENDING: 'P', // 未开始
  COMPLETED: 'F' // 已完赛
})

// 状态 -> 展示文本
export const MATCH_STATUS_TEXT = Object.freeze({
  [MATCH_STATUS.PENDING]: '未开始',
  [MATCH_STATUS.COMPLETED]: '已完赛',
  // 直接映射中文状态
  '未开始': '未开始',
  '已完赛': '已完赛'
})

// 状态 -> 标签 type (Element Plus)
export const MATCH_STATUS_TAG_TYPE = Object.freeze({
  [MATCH_STATUS.PENDING]: 'info',
  [MATCH_STATUS.COMPLETED]: 'success',
  // 直接映射中文状态
  '未开始': 'info',
  '已完赛': 'success'
})

// 获取状态展示文本
export function getMatchStatusText(status){
  return MATCH_STATUS_TEXT[status] || '未开始'
}

// 获取标签类型
export function getMatchStatusTagType(status){
  return MATCH_STATUS_TAG_TYPE[status] || 'info'
}

// =====================================================================
// 比赛事件 (Match Events)
// =====================================================================

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

// 事件 -> 图标映射（Element Plus 图标）
export const MATCH_EVENT_ICON = Object.freeze({
  [MATCH_EVENT_TYPES.GOAL]: 'Football',
  [MATCH_EVENT_TYPES.OWN_GOAL]: 'Football',
  [MATCH_EVENT_TYPES.YELLOW]: 'Warning',
  [MATCH_EVENT_TYPES.RED]: 'CircleClose',
  [MATCH_EVENT_TYPES.SUBSTITUTION]: 'User',
  [MATCH_EVENT_TYPES.PENALTY]: 'Trophy',
  // 兼容中文字符串
  '进球': 'Football',
  '乌龙球': 'Football',
  '黄牌': 'Warning',
  '红牌': 'CircleClose',
  '换人': 'User',
  '点球': 'Trophy',
  // 兼容英文字符串
  'goal': 'Football',
  'own_goal': 'Football',
  'yellow_card': 'Warning',
  'red_card': 'CircleClose',
  'substitution': 'User',
  'penalty': 'Trophy'
})

// 事件类型 -> class（降级兼容传入中文）
export function getMatchEventClass(eventType) {
  return MATCH_EVENT_CLASS[eventType] || MATCH_EVENT_CLASS[MATCH_EVENT_TYPES.GOAL] || ''
}

// 事件类型 -> 图标（降级兼容传入中文）
export function getMatchEventIcon(eventType) {
  return MATCH_EVENT_ICON[eventType] || 'Clock'
}

// =====================================================================
// 比赛类型 (Match Types)
// =====================================================================

// 比赛类型映射（英文 key -> 中文展示）
export const MATCH_TYPE_TEXT = {};

/**
 * 获取比赛类型中文说明
 * @param {string} type 比赛类型代码 (如 'champions-cup')
 * @returns {string} 中文描述，未知时返回 '未知类型'
 */
export function getMatchTypeText(type) {
  return type || '未知类型';
}

// 兼容旧的 domain.js 导出
export const MATCH_TYPES = Object.freeze({});
export const MATCH_TYPE_LABELS = Object.freeze({});
export function getMatchTypeLabel(type) {
  return type || '';
}
