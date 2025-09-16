// 比赛 / 事件 / 状态 标签与文本映射集中管理 (纯映射，不做统计)
import { getMatchStatusTagType, getMatchStatusText } from '@/constants/match'

const MATCH_TYPE_LABELS = Object.freeze({
  'champions-cup': '冠军杯',
  'womens-cup': '巾帼杯',
  'eight-a-side': '八人制比赛'
})

const EVENT_TYPE_LABELS = Object.freeze({
  '进球': '进球',
  '红牌': '红牌',
  '黄牌': '黄牌',
  '乌龙球': '乌龙球',
  'goal': '进球',
  'yellow_card': '黄牌',
  'red_card': '红牌',
  'own_goal': '乌龙球'
})

const EVENT_TAG_TYPE_MAP = Object.freeze({
  '进球': 'success',
  'goal': 'success',
  '黄牌': 'warning',
  'yellow_card': 'warning',
  '红牌': 'danger',
  'red_card': 'danger',
  '乌龙球': 'info',
  'own_goal': 'info'
})

const MATCH_TYPE_TAG_TYPE_MAP = Object.freeze({
  'champions-cup': 'primary',
  'womens-cup': 'success',
  'eight-a-side': 'warning'
})

/**
 * @typedef {Object} ManagementLabelsReturn
 * @property {(type:string)=>string} getMatchTypeLabel
 * @property {(type:string)=>string} getEventTypeLabel
 * @property {(eventType:string)=>import('element-plus').TagProps['type']} getEventTagType
 * @property {(matchType:string)=>import('element-plus').TagProps['type']} getMatchTypeTagType
 * @property {(status:string)=>import('element-plus').TagProps['type']} getStatusTagType
 * @property {(status:string)=>string} getStatusLabel
 */

/**
 * 标签与状态样式映射统一入口。
 * @returns {ManagementLabelsReturn}
 */
export default function useManagementLabels() {
  const getMatchTypeLabel = (type) => MATCH_TYPE_LABELS[type] || type || '未知'
  const getEventTypeLabel = (type) => EVENT_TYPE_LABELS[type] || type || '未知'
  const getEventTagType = (eventType) => EVENT_TAG_TYPE_MAP[eventType] || 'info'
  const getMatchTypeTagType = (matchType) => MATCH_TYPE_TAG_TYPE_MAP[matchType] || 'info'
  const getStatusTagType = (status) => getMatchStatusTagType(status)
  const getStatusLabel = (status) => getMatchStatusText(status)

  return { getMatchTypeLabel, getEventTypeLabel, getEventTagType, getMatchTypeTagType, getStatusTagType, getStatusLabel }
}
