// 聚合导出 admin 目录下的组合函数，便于统一引用
export { default as useManagementFilters } from './useManagementFilters'
export { default as useManagementLabels } from './useManagementLabels'
export { default as usePlayerStats } from './usePlayerStats'

// 其他跨目录通用组合（放在 src/composables 根目录）
export { useScrollHelpers } from '@/composables/scroll/useScrollHelpers.js'
export { default as useMatchTypeMeta } from '@/composables/domain/match/useMatchTypeMeta.js'
export { useAdminBoardPage } from './useAdminBoardPage.js'

// 未来新增：领域相关 meta / helpers 可继续在此集中导出