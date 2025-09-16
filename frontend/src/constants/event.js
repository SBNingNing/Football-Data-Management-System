/**
 * constants/event.js
 * --------------------------------------------------
 * 拆分事件常量 (原 eventTypes.js)，更清晰区分比赛状态与事件
 */
export const EVENT_TYPES = Object.freeze({
  GOAL: '进球',
  OWN_GOAL: '乌龙球',
  YELLOW: '黄牌',
  RED: '红牌',
  SUBSTITUTION: '换人',
  PENALTY: '点球',
  // 英文兼容
  GOAL_EN: 'goal',
  OWN_GOAL_EN: 'own_goal',
  YELLOW_EN: 'yellow_card',
  RED_EN: 'red_card',
  SUBSTITUTION_EN: 'substitution',
  PENALTY_EN: 'penalty'
})

export const EVENT_ICON_MAP = Object.freeze({
  '进球': 'Football',
  '乌龙球': 'Football',
  '黄牌': 'Warning',
  '红牌': 'CircleClose',
  '换人': 'User',
  '点球': 'Trophy',
  goal: 'Football',
  own_goal: 'Football',
  yellow_card: 'Warning',
  red_card: 'CircleClose',
  substitution: 'User',
  penalty: 'Trophy'
})

export const EVENT_CLASS_MAP = Object.freeze({
  '进球': 'event-goal',
  '乌龙球': 'event-own-goal',
  '黄牌': 'event-yellow-card',
  '红牌': 'event-red-card',
  '换人': 'event-substitution',
  '点球': 'event-penalty',
  goal: 'event-goal',
  own_goal: 'event-own-goal',
  yellow_card: 'event-yellow-card',
  red_card: 'event-red-card',
  substitution: 'event-substitution',
  penalty: 'event-penalty'
})

export function getEventIcon(type){ return EVENT_ICON_MAP[type] || 'Clock' }
export function getEventClass(type){ return EVENT_CLASS_MAP[type] || 'event-default' }
