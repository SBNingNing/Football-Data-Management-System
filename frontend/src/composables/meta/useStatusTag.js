/**
 * 状态标签组合函数
 * 提供统一的状态文本和样式映射
 */
import { MATCH_STATUS_TEXT, MATCH_STATUS_TAG_TYPE } from '@/constants/match'

/**
 * 状态标签组合函数
 * @param {Object} customMap 自定义映射配置
 * @param {Object} customMap.textMap 自定义文本映射
 * @param {Object} customMap.tagMap 自定义标签类型映射
 * @param {Object} customMap.fallback 默认值配置
 * @returns {Object} 状态标签相关方法
 */
export function useStatusTag(customMap) {
  // 映射表配置
  const textMap = customMap?.textMap || MATCH_STATUS_TEXT
  const tagMap = customMap?.tagMap || MATCH_STATUS_TAG_TYPE
  const fallback = customMap?.fallback || {
    text: '未开始',
    type: 'info'
  }
  
  /**
   * 解析状态信息
   * @param {string} status 状态值
   * @returns {Object} 状态信息对象
   */
  function resolve(status) {
    return {
      text: textMap[status] || fallback.text,
      type: tagMap[status] || fallback.type
    }
  }
  
  /**
   * 获取状态文本
   * @param {string} status 状态值
   * @returns {string} 状态文本
   */
  function text(status) {
    return resolve(status).text
  }
  
  /**
   * 获取标签类型
   * @param {string} status 状态值
   * @returns {string} 标签类型
   */
  function tagType(status) {
    return resolve(status).type
  }
  
  return {
    resolve,
    text,
    tagType
  }
}
