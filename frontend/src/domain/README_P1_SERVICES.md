# P1 领域服务扩展说明

本文件记录本阶段新增/扩展的前端领域服务、缓存键约定、以及统一变更 (mutation) 与通知策略。

## 新增服务

### seasonsService (`src/domain/season/seasonsService.js`)
功能: 赛季 CRUD + 列表获取。
缓存键:
- `seasons:list`
- `season:<id>`

导出方法:
- `fetchSeasons({ force, cacheTTL })`
- `fetchSeason(seasonId, { force, cacheTTL })`
- `createSeason(payload)`
- `updateSeason(seasonId, payload)`
- `deleteSeason(seasonId)`

### competitionsService (`src/domain/competition/competitionsService.js`)
功能: 赛事 CRUD，支持排序 / 搜索参数 (?sort_by= & search=)。
缓存键:
- `competitions:list:<queryHash>`
- `competition:<id>`

导出方法:
- `fetchCompetitions(params, { force, cacheTTL })`
- `fetchCompetition(id, { force, cacheTTL })`
- `createCompetition(payload)` / `updateCompetition(id, payload)` / `deleteCompetition(id)`

### tournamentCrudService (`src/domain/tournament/tournamentCrudService.js`)
功能: 赛事基本 CRUD + 赛事实例创建/更新 + 快速创建。
缓存键:
- `tournaments:list`
- `tournament:<id>`
- `tournament-instance:<id>`

导出方法:
- `fetchTournaments()` / `fetchTournamentById(id)`
- `createTournament(payload)` / `updateTournament(id, payload)` / `deleteTournament(id)`
- `createTournamentInstance(payload)` / `updateTournamentInstance(id, payload)`
- `quickCreateTournamentInstance(payload)`

注: 统计/聚合依旧由现有 `tournamentService.js` (`fetchTournamentAggregate`) 提供。

### playerHistoryService (`src/domain/player/playerHistoryService.js`)
功能: 球员完整历史、赛季表现、跨赛季对比、转队历史。
路径注意: 后端 blueprint 有 `/api/player-history` 前缀，http 基础 baseURL = `/api`，因此前端使用 `/player-history/...`。
缓存键:
- `playerHistory:complete:<playerId>`
- `playerHistory:season:<playerId>:<seasonId>`
- `playerHistory:teamChanges:<playerId>`
- `playerHistory:compare:<playerIdsHash>:<seasonIdsHash>`

## 统一变更 & 缓存失效 (mutation)
文件: `src/domain/common/mutation.js`

新增支持:
- 精确键: `invalidate: ['teams:list', 'seasons:list']`
- 前缀: `invalidatePrefixes: ['season:', 'playerHistory:complete:']`
- 正则: `invalidatePatterns: [ /^(competitions|tournaments):list/, /^playerHistory:season:/ ]`

示例:
```js
import { mutateAndInvalidate } from '@/domain/common/mutation'
import { createSeason } from '@/domain/season/seasonsService'

async function onSubmit(form){
  const { ok, data, error } = await mutateAndInvalidate(
    () => createSeason(form),
    {
      invalidate: ['seasons:list'],
      invalidatePrefixes: ['tournament:'],
      invalidatePatterns: [/^competitions:list/],
      onSuccess: () => notify.success('赛季创建成功')
    }
  )
}
```

内部实现通过对 cache.setCache / cache.invalidate 打补丁维护 `keySet`，以便执行批量匹配删除；若后续 cache 模块提供 `listKeys()` 可替换该方案。

## 通知封装
文件: `src/utils/notify.js`

提供:
- `notify.success(msg)` / `notify.error(msg)` / `notify.warning(msg)` / `notify.info(msg)`

统一 Element Plus `ElMessage`，后续可切换为全局 Snackbar / Toast 不影响调用层。

## 约定与下一步
- 组件新增/编辑成功后优先通过 `mutateAndInvalidate` 触发相关缓存清理。
- 若某类数据需要模式化失效，优先使用前缀命名 (`<domain>:<entity>:<id>`)，便于前缀或正则批量清理。
- 后续可选: 将缓存键枚举集中到 `src/domain/common/cacheKeys.js`，减少分散常量。

## 错误处理模式回顾
所有服务方法返回 `serviceWrap` 结构: `{ ok, data, error }`；失败时 `error` 为 buildError() 生成，含 `code` 与可选 `raw`，组件层可统一展示。

---
更新时间: 自动生成 (P1 完成阶段)
