# 前端架构说明 (Football Data Management System)

> 目标: 可维护、分层清晰、低耦合、渐进式演进，不破坏既有 UI。

## 目录分层
```
src/
  api/              // (若仍存在) 旧接口层，逐步被 domain service 替换
  domain/
    player/
    team/
    match/
    stats/
  composables/      // 组合式逻辑 (useXxx)
  constants/        // 常量、枚举、标签/事件映射
  utils/            // 通用工具 (httpClient / logger / cache)
  store/            // Pinia 状态 (auth 等)
  components/       // 复用组件 (按业务/区域划分子目录)
  views/            // 页面级组件 (Home / match_detail / ...)
```

## 数据访问策略
- 视图不直接使用 axios；统一经 `utils/httpClient` (封装 baseURL / headers / error normalize / 可选缓存)
- 领域访问集中在 `domain/<entity>/<xxx>Service.js`
- 统一返回结构：`{ ok, data, error }` （所有 service 通过 `serviceWrap` 标准化）
- 缓存策略：通过 `http.get(url, { cache:{ ttl, key, force } })` 实现轻量缓存

## 已实现服务
| 领域 | 文件 | 说明 |
|------|------|------|
| 球员 | `domain/player/playerService.js` | 球员聚合列表/详情（示例化） |
| 球队 | `domain/team/teamService.js` | 球队列表与聚合映射 |
| 比赛 | `domain/match/matchService.js` | 比赛详情聚合 + 记录列表 + 近期比赛 |
| 统计 | `domain/stats/statsService.js` | Dashboard / 排名 / 分组 / 淘汰赛 |

## 常量与枚举
- `constants/match.js`：比赛状态、标签类型、公共状态文本
- `constants/event.js`：事件类型、图标、样式类
- 后续可收敛：比赛类型、颜色主题、角色权限等

统一引用规则：
- 禁止在业务逻辑中直接使用中文事件/状态字符串进行分支；使用 `MATCH_EVENT_TYPES.*` 或组合式 `useStatusTag`。
- UI 展示文案（表头/标签文字）可以直接中文，不必常量化。

## 组合式 (Composables)
| 名称 | 职责 | 备注 |
|------|------|------|
| `useMatchDetail` | 比赛详情聚合加载 (match + players + events) | 内部使用 matchService.fetchMatchAggregate |
| `useMatchRecords` | 比赛记录分页/过滤 | 可扩展缓存、去抖、预取 |
| `useScrollRestore` | 路由切换回来恢复滚动位置 | 已实现基础 memory 策略 |
| `useFeedback` | 全局/局部 loading 与错误反馈统一 | 已实现基础版 (normalizeError/trackPromise) |
| `useAuthGuard` | 路由进入校验 (登录/角色) | beforeEach 中调用 `check(to)` |
| `useHomeDashboard` | 首页多数据块聚合加载与交互 | Home.vue 精简只保留渲染 |

## 状态与反馈规范 (规划)
1. httpClient 统一规范：失败统一 `error = { message, code?, cause? }`
2. 组件内部只负责展示，不直接拼接错误文案（交由反馈层）
3. Loading 分级：
   - 局部数据块 skeleton / spinner
   - 页面级全屏遮罩 (慎用)
   - 后台静默刷新 (不打断 UI)
4. 统一重试机制：
   - 指数退避：1.5x 或 2x 间隔上限
   - 可为 match 详情、关键榜单开启

## 日志策略 (规划)
- 使用 `utils/logger`：debug/info/warn/error
- 域名前缀：`[matchService]`、`[useMatchRecords]`、`[Home]`
- 避免生产环境大量 debug：由环境变量控制输出等级

## 事件/状态映射
- 事件：`constants/event.js` 只负责“类型 → 图标/样式”
- 状态：`constants/match.js` 只负责“状态 → 文本/标签类型”
- 组件内不再硬编码 switch（仅保留极少 fallback）

示例（原硬编码替换）：
```diff
- switch (e.event_type) { case '进球': ... }
+ import { MATCH_EVENT_TYPES } from '@/constants/match'
+ switch (e.event_type) { case MATCH_EVENT_TYPES.GOAL: ... }
```

## Home 页面改造要点
- 统计/榜单：来自 statsService
- 比赛记录：useMatchRecords + matchService
- 状态标签：constants/match
- 近期比赛：matchService.fetchRecentMatches
- 聚合/重试/可见性刷新：`useHomeDashboard`

## match_detail 页面改造要点
- 详情 + 事件二次校正统计：matchService.fetchMatchAggregate
- 事件引用新事件常量；状态统一文本/样式

已替换：事件统计 & 玩家事件 switch 使用 `MATCH_EVENT_TYPES.*`。

## 未来工作建议
1. 引入单元测试 (Vitest) 针对：常量映射、service 错误分支、组合式行为
2. 覆盖更多路由 Meta 说明文档（当前已实现守卫基础版）
3. 构建层面：可加 Prettier + lint-staged（ESLint 已存在）
4. 性能：排行榜分标签延迟加载；事件数据按需轮询
5. 国际化 (i18n)：常量层保留 key，文案集中 message 表
6. 可视化错误追踪：集中上报 normalizeError（Sentry/自建）

## 迁移遗留
- 旧 `eventTypes.js` 已删除（已由 `constants/event.js` 取代）
- 旧 `statusMap.js` 已移除；如需映射扩展统一在 `constants/match.js` 修改
- 动态 `require` 已移除（`Home.vue` → 静态 import）
- 分散首页加载逻辑已迁移到 `useHomeDashboard`

## 统一错误与 Service 包装
`utils/error.js` 提供：
- `buildError(message, code, cause, extra?)`
- `normalizeError(e)` -> 标准结构 `{ message, code, cause?, retryable?, isNormalized }`
- `serviceWrap(asyncFn)` -> 返回 `{ ok:true,data } | { ok:false,error }`
- `withRetry(fn,{ attempts, factor, base, maxDelay })`

Service 模式：
```js
import { serviceWrap, buildError } from '@/utils/error'
export function fetchSomething(){
  return serviceWrap(async () => {
    const res = await http.get('/x')
    if(!res.ok) throw buildError(res.error?.message,'X_FETCH_FAILED',res.error)
    return res.data?.data || []
  })
}
```

组件端消费：
```js
const { ok, data, error } = await fetchSomething()
if(!ok) feedback.pushError(error)
```

## 路由守卫规范
`useAuthGuard.check(to)` 返回：`{ allow:true }` 或 `{ allow:false, redirect, reason }`

路由 meta 支持：
- `requiresAuth: boolean`
- `roles: string[]` （如 `['admin']`）
- `allowGuest: boolean` （只需登录功能但允许游客绕过）

未通过时自动重定向：
```
/login?redirect=<original>&reason=NOT_AUTH
/home?reason=ROLE_FORBIDDEN
```

## 首页聚合组合式 `useHomeDashboard`
职责：集中发起 parallel 请求、错误收集、重试、可见性触发刷新。

暴露：
```
statsData, rankings, playoffBracket, groupRankings,
matchRecords, matchRecordsTotal, recentMatches,
retryCount, isPageRefresh,
loadAllData, fetchMatchRecords, fetchRecentMatches,
handleMatchSearch/Filter/PageChange, refreshData, handleVisibilityChange
```

Home.vue 精简模式：
1. 创建反馈 & 状态标签组合式 (`useFeedback` / `useStatusTag`)
2. 调用 `useHomeDashboard({ feedback })`
3. 模板仅绑定暴露的响应式引用

## 新增模块 Checklist
> 在本项目中添加“一个新功能模块” (例如：赛事评论、积分趋势图) 时遵循：

1. 常量：若存在状态/类型枚举，新建或扩展 `constants/*.js`
2. Service：`domain/<feature>/<feature>Service.js` 使用 `serviceWrap` 返回 `{ ok,data,error }`
3. 组合式：`use<Feature>.js` 负责视图级状态、加载与重试
4. UI：Skeleton / ErrorBanner 统一反馈；不在组件内写复杂 try-catch
5. 错误：通过 `feedback.pushError`；避免直接 `ElMessage.error`（除交互即时提示）
6. 路由：需要保护时配置 `meta.requiresAuth` & `meta.roles`
7. 文档：在“常量与枚举”或“组合式”表格追加条目
8. 命名：文件名全小写中划线或 camelCase；导出主函数 `useXxx` / `fetchXxx`
9. 日志：`[featureService]` / `[useFeature]` 前缀；敏感数据不打日志
10. 性能：并行请求使用 `Promise.all`；高频接口可评估 `cache.ttl`

## 示例：快速模块骨架
```bash
domain/feature/featureService.js
composables/useFeature.js
components/feature/FeaturePanel.vue
constants/feature.js (可选)
```

```js
// domain/feature/featureService.js
import http from '@/utils/httpClient'
import { serviceWrap, buildError } from '@/utils/error'
export function fetchFeatureList(){
  return serviceWrap(async () => {
    const r = await http.get('/feature/list')
    if(!r.ok) throw buildError(r.error?.message,'FEATURE_LIST_FAILED',r.error)
    return r.data?.data || []
  })
}
```

```js
// composables/useFeature.js
import { ref } from 'vue'
import { fetchFeatureList } from '@/domain/feature/featureService'
export function useFeature({ feedback }){
  const list = ref([])
  async function load(){
    feedback?.begin('svc:feature:list')
    try { const { ok, data, error } = await fetchFeatureList(); if(ok) list.value = data; else feedback?.pushError(error) }
    finally { feedback?.end('svc:feature:list') }
  }
  return { list, load }
}
```

## 质量守护点 (执行参考)
- 所有 service 返回值必须含 `ok` 布尔
- 不允许组件内直接调用 axios
- 新增分支逻辑如果出现事件/状态字符串，优先从 constants 导入
- 新增错误必须经过 `buildError` 或 serviceWrap 抛出
- Home 等页面保持“薄”层：逻辑迁移至组合式

---
当前版本：已完成统一错误体系 / 守卫 / 首页瘦身 / 事件状态抽象。后续扩展以 checklist 为准。

## 附录：典型调用示例
```js
// 获取比赛记录
const { ok, data } = await fetchMatchRecords({ token, params:{ page:1 } })
if (ok) console.log(data.records)

// 组合式使用
const { records, load, setFilter } = useMatchRecords()
await load()
setFilter({ status:'ongoing' })
```

---
若需进一步文档(错误反馈/滚动恢复标准实现)，可在 docs/patterns 下追加文件。

## 附录索引（原独立文档已合并）

### A. 统一错误与加载反馈 (原 feedback.md 摘要)
数据分层：
- 数据访问层：httpClient/service 产出 { ok, data, error }
- 反馈聚合层：useFeedback（引用计数 + 错误数组）
- 视图层：监听 isLoading / errors 渲染 Skeleton 或 ErrorBanner

NormalizedError 结构：`{ message, code?, cause?, retryable?, scope?, ts }`
Key 规范：`svc:*` 服务调用 | `view:*` 页面初始化 | `act:*` 用户主动动作
重试策略：指数退避 base=500ms factor=1.8 上限 5s，可封装 withRetry
未来增强：最小显示时长 / 错误去重 / 国际化 message key 化

### B. 滚动恢复与状态标签 (原 scroll_and_tag.md 摘要)
useScrollRestore：`{ save, restore, clear, restoring }` memoryStore + 节流保存 + RAF 重试 10 次
Key 组成建议：`<routeName>:<filtersDigest>` 确保不同筛选上下文独立
待扩展：sessionStorage strategy / 动画恢复 / 多容器
useStatusTag（待实现）：对 constants/match 的文本与标签类型包装，提供 `resolve/text/tagType`

### C. 未使用资源标注策略 (原 unused-assets.md 摘要)
保留原因：防止误删计划中组件/样式。约定注释块 `@preserve-unused` 包含 reason / added / (optional remove-after)。
扫描方式：grep `@preserve-unused`；发布前脚本审计，超过 remove-after 未引用即清理。
现状：当前无需要保留的未使用组件；后续新增时参考此规范。

---
注：若未来内容再次显著扩展，可按需重新拆分文档；当前阶段合并以减少文件数量并集中入口。
