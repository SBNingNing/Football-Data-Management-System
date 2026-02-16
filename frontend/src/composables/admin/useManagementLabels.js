/**
 * 管理端标签与文本映射组合函数
 * 提供统一的标签样式和文本映射功能
 */
import { getMatchStatusTagType, getMatchStatusText } from '@/utils/constants'

// 比赛类型标签映射
const MATCH_TYPE_LABELS = Object.freeze({
  'champions-cup': '冠军杯',
  'womens-cup': '巾帼杯',
  'eight-a-side': '八人制比赛'
})

// 事件类型标签映射
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

// 事件标签类型映射
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

// 比赛类型标签类型映射
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
 * 管理端标签与状态样式映射组合函数
 * @returns {ManagementLabelsReturn}
 */
export default function useManagementLabels() {
  /**
   * 获取比赛类型标签
   * @param {string} type 比赛类型
   * @returns {string} 标签文本
   */
  const getMatchTypeLabel = (type) => {
    return MATCH_TYPE_LABELS[type] || type || '未知'
  }

  /**
   * 获取事件类型标签
   * @param {string} type 事件类型
   * @returns {string} 标签文本
   */
  const getEventTypeLabel = (type) => {
    return EVENT_TYPE_LABELS[type] || type || '未知'
  }

  /**
   * 获取事件标签类型
   * @param {string} eventType 事件类型
   * @returns {import('element-plus').TagProps['type']} 标签类型
   */
  const getEventTagType = (eventType) => {
    return EVENT_TAG_TYPE_MAP[eventType] || 'info'
  }

  /**
   * 获取比赛类型标签类型
   * @param {string} matchType 比赛类型
   * @returns {import('element-plus').TagProps['type']} 标签类型
   */
  const getMatchTypeTagType = (matchType) => {
    return MATCH_TYPE_TAG_TYPE_MAP[matchType] || 'info'
  }

  /**
   * 获取状态标签类型
   * @param {string} status 状态
   * @returns {import('element-plus').TagProps['type']} 标签类型
   */
  const getStatusTagType = (status) => {
    return getMatchStatusTagType(status)
  }

  /**
   * 获取状态标签文本
   * @param {string} status 状态
   * @returns {string} 标签文本
   */
  const getStatusLabel = (status) => {
    return getMatchStatusText(status)
  }

  return {
    getMatchTypeLabel,
    getEventTypeLabel,
    getEventTagType,
    getMatchTypeTagType,
    getStatusTagType,
    getStatusLabel
  }
}
