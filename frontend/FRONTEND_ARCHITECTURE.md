# Football Data Management System - 前端架构文档

## 1. 架构概览

本项目前端基于 **Vue 3** 生态构建，采用 **组件化** 与 **组合式 API (Composition API)** 相结合的开发模式。
架构设计上正在向 **领域驱动 (Domain-Driven)** 风格演进，旨在实现 UI 表现与业务逻辑的分离。

### 核心技术栈
- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **UI 组件库**: Element Plus
- **路由管理**: Vue Router 4
- **状态管理**: Pinia
- **HTTP 客户端**: Axios (封装于 `httpClient`)
- **样式处理**: CSS Variables / Scoped CSS

---

## 2. 目录结构与分层说明

前端代码位于 `src/` 目录下，各层级职责划分如下：

```text
frontend/src/
├── api/             # [接口层] 定义与后端通信的 HTTP 请求方法
├── assets/          # [资源层] 静态资源、全局样式 (CSS Variables)
├── components/      # [组件层] 可复用的 UI 组件（按业务模块划分）
├── composables/     # [逻辑层] 组合式函数，封装业务逻辑与状态
│   ├── domain/      # 核心领域逻辑 (Player, Team, Match)
│   ├── ui/          # UI 相关逻辑 (Toast, Loading)
│   └── ...
├── router/          # [路由层] 页面路由定义
├── store/           # [状态层] 全局状态管理 (Pinia Modules)
├── utils/           # [工具层] 通用工具函数 (HTTP, Logger, Formatters)
├── views/           # [视图层] 页面级组件，组装 Components 与 Composables
└── App.vue          # 根组件
```

---

## 3. 各层级详细说明

### 3.1 接口层 (API)
- **位置**: `src/api/`
- **职责**: 
  - 封装 RESTful API 请求。
  - **不包含** 业务逻辑状态，只负责透传参数和返回 Promise。
  - 例如 `teams.js` 包含 `fetchTeams`, `createTeam` 等纯函数。

### 3.2 逻辑层 (Composables)
- **位置**: `src/composables/`
- **职责**:
  - **Domain Logic**: 在 `domain/` 下按业务领域（如 `useTeamHistory.js`）封装数据获取、处理、错误处理逻辑。
  - **UI/Feature Logic**: 封装通用的功能逻辑（如 `useScroll`, `useSelection`）。
  - 连接 API 层与 UI 层，是“ViewModel”角色的主要承担者。

### 3.3 状态层 (Store)
- **位置**: `src/store/`
- **职责**:
  - 管理跨组件/跨页面的全局状态（如：当前登录用户 `auth`，数据缓存 `teamHistory`）。
  - 使用 Pinia 定义 Store，支持模块化拆分。
  - 处理需要持久化或频繁共享的数据。

### 3.4 组件层 (Components)
- **位置**: `src/components/`
- **职责**:
  - **展示型组件 (Dumb Components)**: 负责渲染数据，通过 Props 接收数据，Emit 发出事件。
  - 按模块组织：`home/`, `match/`, `player/`, `team/`, `admin/`。
  - 例如 `TeamSeasonRecords.vue` 只负责展示赛季记录表格，不直接调用 API。

### 3.5 视图层 (Views)
- **位置**: `src/views/`
- **职责**:
  - 页面入口，对应路由配置。
  - 负责**组装**：引入 Store、Composables 和 Components。
  - 负责布局结构，但不包含过多的样式细节（样式下沉到组件或全局 CSS）。

### 3.6 工具层 (Utils)
- **位置**: `src/utils/`
- **关键模块**:
  - `httpClient.js`: 深度封装 Axios，处理拦截器、Token 注入、全局错误处理、响应解包。
  - `logger.js`: 前端日志记录器。
  - `formatters.js`: 数据格式化工具（日期、比分等）。

---

## 4. 数据流向示例

以 **"查看球队详情"** 为例：

1.  **View (`views/team/team_history.vue`)**:
    - 页面加载，调用 `useTeamHistoryPage`。
2.  **Composable (`composables/domain/team/useTeamHistoryPage.js`)**:
    - 初始化，解析路由参数中的球队 ID。
    - 调用 `useTeamHistory` 的 `load` 方法。
3.  **Composable (`composables/domain/team/useTeamHistory.js`)**:
    - 调用 Store 或 API 获取数据。
    - 处理 `loading` 和 `error` 状态。
4.  **Store (`store/modules/teamHistory.js`)**:
    - 检查缓存。若无缓存，调用 API 层。
5.  **API (`api/teams.js`)**:
    - 发送 HTTP 请求 `GET /api/teams/{id}`。
6.  **UI Update**:
    - 数据返回通过 Reactivity 系统自动更新 View 中的 `TeamBasicInfo` 和 `TeamSeasonRecords` 组件。

---

## 5. 环境配置与启动

### 5.1 前置要求
- Node.js 16+
- npm 或 yarn 或 pnpm

### 5.2 安装依赖
在 `frontend/` 目录下执行：

```bash
npm install
```

### 5.3 环境变量
检查 `.env.development` 文件：

```ini
VITE_API_BASE_URL=/api
```

### 5.4 启动前端 (开发模式)

```bash
npm run dev
```

- 服务默认运行在 `http://localhost:3000` (或 5173，视 vite 配置而定)。
- 此时 Vite 会开启反向代理（Proxy），将 `/api` 请求转发给后端（默认 `http://localhost:5000`）。

### 5.5 构建生产版本

```bash
npm run build
```
构建产物将输出到 `dist/` 目录。
