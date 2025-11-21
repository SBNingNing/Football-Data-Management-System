// 域模型常量集中定义，避免各组件散落魔法字符串
// 后续可按需拆分为多个文件（matchTypes.js, statuses.js 等）

export const MATCH_TYPES = Object.freeze({});

export const MATCH_TYPE_LABELS = Object.freeze({});

export function getMatchTypeLabel(type) {
  return type || '';
}
