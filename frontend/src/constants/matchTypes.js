/**
 * =====================================================================
 * 文件: matchTypes.js
 * 功能: 统一管理比赛类型(code) 与 中文展示文案的映射，避免在各处硬编码。
 * 典型来源: 后端返回字段 match_type / matchType。
 * 扩展方式: 新增类型时直接补充 MATCH_TYPE_TEXT；页面无需改动。
 * =====================================================================
 */
// 比赛类型映射（英文 key -> 中文展示）
export const MATCH_TYPE_TEXT = {
  'champions-cup': '冠军杯',
  'womens-cup': '巾帼杯',
  'eight-a-side': '八人制比赛'
};

/**
 * 获取比赛类型中文说明
 * @param {string} type 比赛类型代码 (如 'champions-cup')
 * @returns {string} 中文描述，未知时返回 '未知类型'
 */
export function getMatchTypeText(type) {
  return MATCH_TYPE_TEXT[type] || '未知类型';
}
