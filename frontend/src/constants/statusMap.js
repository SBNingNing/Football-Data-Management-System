/**
 * 比赛状态映射 (Match Status Mapping)
 * ------------------------------------------------------------
 * 设计目标:
 * 1. 统一后端原始状态码 (可能为单字母 / 缩写) 到前端可读、语义明确的内部代码
 * 2. 提供最终展示给用户的本地化中文文案，集中管理，减少多处硬编码
 * 3. 允许新增状态时低风险扩展
 *
 * 当前支持后端原始状态:
 * - 'P' : 未开始 (pending/upcoming)
 * - 'O' : 进行中 (ongoing)
 * - 'F' : 已结束 (finished/completed)
 *
 * 导出常量:
 * - RAW_STATUS_TO_CODE: 原始 -> 内部统一代码
 * - STATUS_TEXT: 内部统一代码 -> 中文显示
 *
 * 提供方法:
 * - mapStatus(raw): 输入后端原始值，输出统一代码；未知回退 'completed' (保持界面稳定，不显示空状态)
 * - statusText(code): 输入统一代码返回中文；未知回退 '已结束'
 *
 * 扩展规范:
 * - 若后端新增例如 'S'(暂停) 或 'C'(取消)，只需:
 *   1) RAW_STATUS_TO_CODE 中加入映射: 'S': 'suspended'
 *   2) STATUS_TEXT 中加入: 'suspended': '已暂停'
 *   3) 视图层无需改动 (除非需要特殊样式)
 *
 * 维护建议:
 * - mapStatus 默认回退策略可根据业务改为 'upcoming' 或独立 'unknown'，但需同步 UI 处理逻辑
 * - 若做 i18n，多语言文本仅替换 STATUS_TEXT 值或者通过 key -> i18n lookup
 */
// 比赛状态后端 -> 前端统一枚举
export const RAW_STATUS_TO_CODE = {
  'P': 'upcoming',
  'O': 'ongoing',
  'F': 'completed'
};

export const STATUS_TEXT = {
  'upcoming': '未开始',
  'ongoing': '进行中',
  'completed': '已结束'
};

/**
 * 将后端原始状态码映射为前端统一内部代码
 * @param {string} raw 后端原始状态码 (例如 'P','O','F')
 * @returns {string} 统一代码(upcoming|ongoing|completed)；未知回退 'completed'
 */
export function mapStatus(raw) {
  return RAW_STATUS_TO_CODE[raw] || 'completed';
}

/**
 * 获取内部统一代码对应的中文展示文本
 * @param {string} code 统一代码 (upcoming|ongoing|completed)
 * @returns {string} 中文文本；未知回退 '已结束'
 */
export function statusText(code) {
  return STATUS_TEXT[code] || '已结束';
}
