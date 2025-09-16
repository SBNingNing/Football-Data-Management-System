/**
 * Global Cache Key Registry
 * ---------------------------------------------
 * 聚合各领域缓存键生成，避免各 service 内部硬编码字符串，便于后期统一失效与观测。
 * 约定: 常量大写 + 工厂函数使用小写驼峰。
 */

// Season
export const SEASON_KEYS = {
  LIST: 'seasons:list',
  one: (id) => `season:${id}`
}

// Competition
const hashQuery = (q) => {
  if(!q) return 'default'
  return Object.keys(q).sort().map(k=>`${k}=${q[k]}`).join('&') || 'default'
}
export const COMPETITION_KEYS = {
  list: (queryObj) => `competitions:list:${hashQuery(queryObj)}`,
  one: (id) => `competition:${id}`
}

// Tournament
export const TOURNAMENT_KEYS = {
  LIST: 'tournaments:list',
  one: (id) => `tournament:${id}`,
  instance: (id) => `tournament-instance:${id}`
}

// Player history (示例，可按真实接口扩展)
export const PLAYER_HISTORY_KEYS = {
  complete: (playerId) => `player-history:complete:${playerId}`,
  season: (playerId, seasonId) => `player-history:season:${playerId}:${seasonId}`,
  compare: (ids) => `player-history:compare:${[].concat(ids).sort().join(',')}`,
  teamChanges: (playerId) => `player-history:team-changes:${playerId}`
}

// 通用聚合 (可用于调试/枚举所有 key 工厂)
export const ALL_CACHE_KEY_FACTORIES = {
  SEASON_KEYS,
  COMPETITION_KEYS,
  TOURNAMENT_KEYS,
  PLAYER_HISTORY_KEYS
}
