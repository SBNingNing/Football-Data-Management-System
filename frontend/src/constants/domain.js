// 域模型常量集中定义，避免各组件散落魔法字符串
// 后续可按需拆分为多个文件（matchTypes.js, statuses.js 等）

export const MATCH_TYPES = Object.freeze({
  CHAMPIONS_CUP: 'champions-cup',
  WOMENS_CUP: 'womens-cup',
  EIGHT_A_SIDE: 'eight-a-side'
});

export const MATCH_TYPE_LABELS = Object.freeze({
  [MATCH_TYPES.CHAMPIONS_CUP]: '冠军杯',
  [MATCH_TYPES.WOMENS_CUP]: '巾帼杯',
  [MATCH_TYPES.EIGHT_A_SIDE]: '八人制比赛'
});

export function getMatchTypeLabel(type) {
  return MATCH_TYPE_LABELS[type] || '';
}
