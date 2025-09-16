# 后端架构说明 (Football Data Management System)

> 目标: 可维护、分层清晰、低耦合、渐进式演进，不破坏既有 API 契约。

## 目录分层
```
backend/app/
  routes/        // 路由层：HTTP 处理、入参与出参封装（保持 envelope）
  services/      // 服务层：业务逻辑、聚合、事务边界
  middleware/    // 中间件：验证、上下文、错误处理、统计增强
  utils/         // 工具层：logger/时间/格式化/模块工具
  schemas/       // Pydantic v2 输入/输出模型（统一 model_dump）
  models/        // SQLAlchemy ORM 模型
  config.py      // 环境配置（Development/Production/Testing）
  database.py    // 数据库初始化与会话管理
  extensions.py  // db/cors/jwt 等第三方扩展
  __init__.py    // 应用工厂 create_app
```

## 数据访问与响应策略
- 路由层不直接书写业务逻辑；只做入参校验与响应封装。
- 统一响应结构（envelope）：`{ status, data, message }`，兼容前端既有消费方式。
- Pydantic v2 模型统一使用 `model_dump(by_alias=True)` 序列化。

## 运行环境与依赖
- Python：建议 3.11/3.12（当前虚拟环境已验证）
- 必要依赖：
  - Flask>=2, Flask-SQLAlchemy>=3, Flask-JWT-Extended>=4, Flask-CORS
  - SQLAlchemy>=1.4, PyMySQL>=1.0
  - Pydantic>=2,<3（已从 v1 迁移至 v2）
  - email-validator（EmailStr 运行时依赖）
- 其他：
  - 日志集中在 `utils/logger.py`（统一根日志器、文件轮转）
  - Windows 开发模式采用 stat 重载，避免重复扫描

## 模块与职责
| 领域 | 路由 | Schema | 服务/中间件/工具 | 说明 |
|------|------|--------|------------------|------|
| 认证与用户 | routes/auth.py | schemas/auth.py, schemas/user.py | JWT（Flask-JWT-Extended） | 登录/注册/游客登录，EmailStr 校验 |
| 赛季 | routes/seasons.py | schemas/seasons.py | services/season_service.py, middleware/season_middleware.py | CRUD + 分页 |
| 比赛 | routes/matches.py | schemas/matches.py | services/match_service.py, middleware/match_middleware.py | 创建/更新/完赛/查询/记录 |
| 事件 | routes/events.py | schemas/events.py | services/event_service.py, middleware/event_middleware.py | 创建/更新/删除/列表 |
| 球队 | routes/teams.py | schemas/teams.py | services/team_service.py, middleware/team_middleware.py, utils/team_utils.py | CRUD/查询 |
| 球员 | routes/players.py | schemas/player.py | services/player_service.py, middleware/player_middleware.py | CRUD/查询 |
| 锦标赛 | routes/tournaments.py | schemas/tournaments.py | services/tournament_service.py, middleware/tournament_middleware.py, utils/tournament_utils.py | CRUD/实例/查询 |
| 统计 | routes/stats.py | schemas/stats.py | services/stats_service.py, middleware/stats_middleware.py, utils/stats_utils.py | 概览/排行/赛事统计 |
| 球队历史 | routes/team_history.py | schemas/team_history.py | services/team_history_service.py, middleware/team_history_middleware.py, utils/team_history_utils.py | 历史/赛季表现/参赛史 |
| 球员历史 | routes/player_history.py | schemas/player_history.py | services/player_history_service.py, middleware/player_history_middleware.py | 历史/赛季表现/转队 |
| 竞赛/联赛 | routes/competitions.py | schemas/competitions.py | — | 查询/排行 |
| 健康检查 | routes/health.py | — | — | 健康状态 |

## 统一错误与日志
- 错误：路由-中间件-服务分层处理；对外保持 `{ status:'error', message, data? }`。
- 日志：`utils/logger.py` 统一输出，敏感信息不落日志；域名前缀建议如 `[statsService]`、`[authRoutes]`。

## 模块核心功能说明

### 认证与用户（auth）
- 登录/注册/游客登录：签发与验证 JWT，最小用户信息读取（/me）。
- 输入校验：邮箱使用 `EmailStr`（依赖 email-validator）。
- 响应契约：`{ status, data:{ token, user }, message }`；错误时返回 `ErrorResponse`。

### 赛季（seasons）
- CRUD 与分页列表：创建/更新/删除赛季；分页返回 `Page[SeasonOut]`。
- 约束校验：ID 存在性、名称/时间区间等中间件校验。
- 响应契约：统一 envelope，分页含 `PageMeta(pageNum,pageSize,total)`。

### 比赛（matches）
- 比赛创建/更新/完赛：写入基础信息与状态流转。
- 查询与记录：按条件检索、提供比赛记录列表。
- 约束与联动：关联球队/球员存在性校验，必要的业务规则验证。

### 事件（events）
- 事件创建/更新/删除：与比赛关联，支持多类型事件（进球、犯规等）。
- 列表/查询：按比赛或条件过滤返回事件集合。
- 一致性与回放：为前端提供可重建时间线的数据结构。

### 球队（teams）
- CRUD/查询：基础档案、检索与聚合映射能力。
- 辅助工具：`utils/team_utils.py` 提供常用格式化/映射工具。
- 与比赛/历史的联动：作为外键被其他模块引用，需保证引用完整性。

### 球员（players）
- CRUD/查询：球员档案维护与检索。
- 数据约束：号码、位置、所属队等业务校验。
- 历史联动：与球员历史模块在服务层协同聚合。

### 锦标赛（tournaments）
- 实例管理：创建赛事、阶段管理、参赛队管理。
- 查询：赛事列表、实例详情等。
- 工具支持：`utils/tournament_utils.py` 提供结构化帮助。

### 统计（stats）
- 概览/排行榜/赛事统计：面向首页与详情页的数据聚合。
- Rankings：`schemas/stats.py` 使用 `RootModel` 封装分组结构，前端直接消费。
- 性能与缓存：可在中间件层附加日志与（可选）缓存策略。

### 球队历史（team_history）
- 团队历年表现：完整历史、赛季表现、对比与参赛史。
- 统一输出：面向前端视图的结构化汇总，便于图表/表格直接使用。

### 球员历史（player_history）
- 玩家职业轨迹：完整历史、赛季表现、转队记录。
- 与当前状态对比：为详情页提供纵向对比数据。

### 竞赛/联赛（competitions）
- 查询/排行聚合：联赛/杯赛信息查询与衍生榜单。
- 与赛季/赛事联动：作为维度项参与其他模块的查询过滤。

### 健康检查（health）
- 轻量就绪探针：返回应用在线与依赖可用性基本判断。
- 可用于外部负载或监控系统健康探测。

## Pydantic v2 Schema 能力（新增与迁移要点）
- 基类与配置
  - 统一基类：`SchemaBase`，使用 `model_config = ConfigDict(...)`。
  - 字段别名：序列化统一 `model_dump(by_alias=True)`，对齐前端字段期望。
- 常用泛型与响应封装
  - `Success[T]`：成功响应 envelope；`status` 字段使用 `Literal['success']`（v2 写法）。
  - `ErrorResponse`：错误响应 envelope；`status` 使用 `Literal['error']`；`message` 为用户可读信息。
  - `Page[T]` 与 `PageMeta`：分页统一结构（pageNum/pageSize/total）。
- Rankings 的 RootModel
  - 在 `schemas/stats.py` 中引入 `Rankings: RootModel[Dict[str, RankingsBlock]]`，替代 v1 的 `__root__` 写法。
  - `RankingsBlock`、`PointsRankingItem` 等子结构维持不变，便于前端消费。
- 其它 v2 关键迁移
  - `.dict()` → `.model_dump()`；`.json()` → `.model_dump_json()`。
  - `class Config` → `model_config = ConfigDict(...)`。
  - `Field(const=True)` → `typing.Literal[...]`。
  - `__root__` → `pydantic.RootModel`。
- Email 校验
  - `EmailStr` 依赖 `email-validator`（已在 requirements 中声明）。

## 最小运行与验证
- 应用工厂：`__init__.py:create_app`
- 启动脚本：`backend/run.py`（按环境变量选择配置）
- 健诊脚本（新增）：`backend/tests/schema_sanity.py`
  - 覆盖：`SeasonOut` 序列化、`RegisterIn` 邮箱校验、`Rankings` RootModel 解析
  - 运行通过即表明 v2 核心序列化/校验链路可用

## 质量守护点（执行参考）
- 所有路由响应需保持三段式 envelope。
- Schema 序列化统一 `model_dump(by_alias=True)`；避免直接返回 ORM 对象。
- 服务层避免泄露数据库会话；事务边界在服务层控制。
- 日志输出遵循等级与前缀约定；生产环境关闭 verbose。

## 迁移遗留与后续建议
- 已完成：核心 schema 与路由迁移至 Pydantic v2；`stats` 使用 RootModel；新增最小健诊脚本。
- 待补充（可选）：
  - 更广的单元测试覆盖（Auth/Seasons/Matches 正向与错误分支）。
  - 在 docs/ 或 refactoring_summary 下追加 “Pydantic v2 迁移记要” 细化示例。
- 兼容性说明：保留原有 envelope、字段别名与前端依赖契约，前端无需改动即可兼容。

---
如需更细的模块行为与字段定义，请查阅 `schemas/*` 与对应 `routes/*` 的实现。
