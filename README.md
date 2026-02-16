# Football Data Management System (足球数据管理系统)

## 1. 系统简介

本项目是一个现代化的全栈足球数据管理系统，旨在高效管理校园或业余足球联赛的各项数据，包括赛事、球队、球员、比赛记录及详细的技术统计。系统为管理员提供便捷的数据录入工具，同时为访客提供丰富的数据查询与可视化展示。

---

## 2. 整体架构设计

本系统采用 **前后端分离 (B/S)** 架构，通过标准化的 RESTful API 进行通信。前后端各司其职，遵循关注点分离原则。

```mermaid
graph TD
    User[用户/管理员] -->|HTTP/HTTPS| Frontend[前端 (Vue 3 SPA)]
    Frontend -->|RESTful API| Backend[后端 (Flask API)]
    Backend -->|SQLAlchemy| DB[(MySQL 8.0)]
```

### 2.1 后端架构 (Backend)
后端基于 **Python Flask** 框架构建，严格遵循 **分层架构 (Layered Architecture)**，确保业务逻辑的清晰与可维护性。

*   **核心技术栈**: Flask, SQLAlchemy, Pydantic v2, MySQL, JWT
*   **架构分层**:
    *   **表现层 (Routes)**: 位于 `app/routes/`。负责接收 HTTP 请求，解析参数，调用 Service 层处理业务，并将结果封装成标准 JSON 响应。此处不包含任何复杂业务逻辑。
    *   **业务层 (Services)**: 位于 `app/services/`。系统的核心大脑，封装了所有的业务规则（如积分计算、胜负判定）、跨模块数据聚合以及数据库事务管理。
    *   **数据传输层 (Schemas)**: 位于 `app/schemas/`。基于 Pydantic v2 构建，负责严格的输入数据校验（Request Body/Query）和输出数据序列化（Response），确保接口契约的稳定性。
    *   **持久层 (Models)**: 位于 `app/models/`。基于 SQLAlchemy ORM 定义，负责数据库表结构的映射以及底层的数据库原子操作。
    *   **中间件层 (Middleware)**: 位于 `app/middleware/`。处理横切关注点，如 JWT 身份验证、全局异常捕获、请求日志记录和 CORS 安全配置。
*   **详情文档**: 请参阅 [backend/BACKEND_ARCHITECTURE.md](backend/BACKEND_ARCHITECTURE.md)

### 2.2 前端架构 (Frontend)
前端基于 **Vue 3** 生态构建，采用 **组合式 API (Composition API)** 开发模式，并正在向 **领域驱动 (Domain-Driven)** 风格演进。

*   **核心技术栈**: Vue 3, Vite, Pinia, Element Plus, Axios
*   **架构分层**:
    *   **视图层 (Views)**: 位于 `src/views/`。作为页面级的路由入口，负责组装 Components 和 Composable 逻辑，决定页面的整体布局。
    *   **组件层 (Components)**: 位于 `src/components/`。主要由纯展示组件（Dumb Components）组成，负责数据的渲染与用户交互事件的抛出，尽量不包含业务状态。
    *   **逻辑层 (Composables)**: 位于 `src/composables/`。承担 ViewModel 的角色，按业务领域（如 `domain/team`）封装状态、API 调用和数据处理逻辑，实现 UI 与逻辑的解耦。
    *   **状态层 (Store)**: 位于 `src/store/`。基于 Pinia 实现，用于管理跨组件共享的全局状态（如用户信息、缓存数据），支持模块化拆分。
    *   **接口层 (API)**: 位于 `src/api/`。对 Axios 进行二次封装，定义纯粹的后端接口调用方法，不包含任何业务判断。
    *   **工具层 (Utils)**: 位于 `src/utils/`。提供 HTTP 请求拦截、日志记录、格式化工具等基础设施支持。
*   **详情文档**: 请参阅 [frontend/FRONTEND_ARCHITECTURE.md](frontend/FRONTEND_ARCHITECTURE.md)

---

## 3. 系统核心特性

*   **模块化设计**: 比赛、球队、球员、统计等模块高度解耦。
*   **强类型校验**: 后端使用 Pydantic 确保数据输入输出的严格类型安全。
*   **领域驱动演进**: 前端逻辑层（Composables）按业务领域划分，实现 UI 与逻辑分离。
*   **安全性**: 完整的 JWT 认证流程，配合安全中间件与请求头管理。

---

## 4. 快速启动

### 方法一：一键启动 (推荐 Windows 开发环境)
项目根目录下提供了 `install_and_run.py` 脚本，可协助安装依赖并同时启动前后端服务。

```bash
python install_and_run.py
```

### 方法二：分别启动

**启动后端**:
```bash
cd backend
# 激活虚拟环境 (可选)
pip install -r requirements.txt
python run.py
# 服务运行在 http://localhost:5000
```

**启动前端**:
```bash
cd frontend
npm install
npm run dev
# 服务运行在 http://localhost:3000
```

---

## 5. 待改进与优化项 (TODO)

系统目前虽然运行稳定，但为应对未来扩展，以下架构问题需优先解决：

| 优先级 | 问题描述 | 潜在风险 | 建议修改方案 |
| :--- | :--- | :--- | :--- |
| **最高** | **变量命名风格不统一** | 前端使用 CamelCase（小驼峰），后端使用 SnakeCase（下划线），通过 `jsonify` 硬编码返回。一旦字段增多，序列化/反序列化极易出错，也增加了前端判空的复杂度。 | **统一接口契约**：<br>1. **推荐**：前端 HttpClient 统一配置请求/响应拦截器，自动将所有下划线转为驼峰。<br>2. **替代**：后端 Pydantic Schema 配置 `alias_generator`，输出时自动转驼峰。 |
| **高** | **Service 层缺乏事务控制** | 业务逻辑中往往涉及多张表操作（如：比赛结束 -> 插入 Match 记录 -> 插入 PlayerStats -> 更新 Team 积分）。目前若第 3 步失败，前 2 步的数据却已写入，导致数据不一致（脏数据）。 | **引入原子性事务 (Atomic Transaction)**：<br>推荐使用上下文管理器模式：<br>`with db.session.begin():`<br>&nbsp;&nbsp;`service.create_match()`<br>确保要么全成功，要么全回滚。 |
| **中** | **N+1 查询性能隐患** | Service 层在 `for` 循环中访问关联对象（如：遍历 100 场比赛，每场比赛里再去查一次 `match.away_team.name`）。这将产生 1+100 条 SQL 查询，页面响应极慢。 | **优化 ORM 查询策略**：<br>使用 SQLAlchemy 的 **Eager Loading (预加载)**：<br>`query.options(joinedload(Match.away_team))`<br>将多次查询合并为 1 次 JOIN 查询。 |
| **中** | **前端错误处理与状态复位** | 在 `useTeamHistory` 等 Composable 中，若 `await fetch()` 抛出异常，`loading.value` 可能未被正确重置为 `false`，导致页面一直显示加载动画（假死），用户无法重试。 | **增强鲁棒性 (Robustness)**：<br>1. 只要有 `loading=true`，必须配合 `try...finally { loading=false }` 确保一定会结束。<br>2. 引入 **全局错误边界 (Error Boundary)** 组件，捕获未处理的 Promise 异常。 |
| **中** | **前端缺乏数据缓存** | 每次点击“球队详情”都重新请求 API。对于历史数据这种低频变更的内容，重复请求浪费带宽且体验卡顿。 | **实现客户端缓存 (Client-side Caching)**：<br>在 Pinia Store 中引入简单的 TTL 缓存机制：<br>`if (cache[id] && (now - time < 60s)) return cache[id]`<br>优先返回内存中的数据。 |
