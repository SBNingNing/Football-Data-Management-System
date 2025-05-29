# 足球数据管理系统

## 项目概述
足球数据管理系统是一个基于Spring Boot + MySQL后端与Vue.js + Element Plus前端的全栈应用程序，专为校园足球赛事管理设计。该系统可以管理球员、球队、赛事、赛季、比赛和事件等数据，提供全面的统计和管理功能。

## 技术栈
### 后端
- Spring Boot 2.7.x
- Spring Data JPA
- Spring Security
- MySQL 8.x
- Maven

### 前端
- Vue.js 3
- Element Plus
- Axios
- Vue Router
- Vuex/Pinia

## 系统架构

### 整体架构
```
足球数据管理系统
│
├── 前端（Vue.js + Element Plus）
│   ├── 页面视图（View）
│   ├── 组件（Components）
│   ├── 路由（Router）
│   ├── 状态管理（Store）
│   └── API调用（Services）
│
└── 后端（Spring Boot + MySQL）
    ├── 控制器层（Controller）
    ├── 服务层（Service）
    ├── 数据访问层（Repository）
    ├── 实体层（Entity）
    ├── DTO层（Data Transfer Objects）
    └── 安全层（Security）
```

### 后端架构
```
src/main/java/com/football
│
├── controller       # REST API控制器
│   ├── PlayerController
│   ├── TeamController
│   ├── MatchController
│   ├── EventController
│   ├── TournamentController
│   ├── SeasonController
│   └── UserController
│
├── service          # 业务逻辑层
│   ├── PlayerService
│   ├── TeamService
│   ├── MatchService
│   ├── EventService
│   ├── TournamentService
│   ├── SeasonService
│   └── UserService
│
├── repository       # 数据访问层
│   ├── PlayerRepository
│   ├── TeamRepository
│   ├── MatchRepository
│   ├── EventRepository
│   ├── TournamentRepository
│   ├── SeasonRepository
│   └── UserRepository
│
├── model/entity     # 数据实体
│   ├── Player
│   ├── Team
│   ├── Match
│   ├── Event
│   ├── Tournament
│   ├── Season
│   └── User
│
├── dto              # 数据传输对象
│   ├── PlayerDTO
│   ├── TeamDTO
│   ├── MatchDTO
│   ├── EventDTO
│   ├── TournamentDTO
│   ├── SeasonDTO
│   └── UserDTO
│
├── config           # 配置类
│   ├── SecurityConfig
│   └── WebConfig
│
├── exception        # 异常处理
│   ├── ResourceNotFoundException
│   ├── BadRequestException
│   └── GlobalExceptionHandler
│
└── util             # 工具类
    ├── JwtUtil
    └── PaginationUtil
```

### 前端架构
```
src/
│
├── assets/          # 静态资源
│
├── components/      # 公共组件
│   ├── common/      # 通用组件
│   ├── player/      # 球员相关组件
│   ├── team/        # 球队相关组件
│   ├── match/       # 比赛相关组件
│   ├── event/       # 事件相关组件
│   ├── tournament/  # 赛事相关组件
│   └── season/      # 赛季相关组件
│
├── views/           # 页面视图
│   ├── dashboard/   # 仪表盘
│   ├── player/      # 球员管理
│   ├── team/        # 球队管理
│   ├── match/       # 比赛管理
│   ├── event/       # 事件管理
│   ├── tournament/  # 赛事管理
│   ├── season/      # 赛季管理
│   ├── statistics/  # 数据统计
│   ├── user/        # 用户管理
│   └── auth/        # 认证相关页面
│
├── router/          # 路由配置
│
├── store/           # 状态管理
│   ├── modules/     # 模块化状态
│   └── index.js     # 全局状态管理
│
├── services/        # API服务
│   ├── api.js       # API基础配置
│   ├── playerService.js
│   ├── teamService.js
│   ├── matchService.js
│   ├── eventService.js
│   ├── tournamentService.js
│   ├── seasonService.js
│   └── userService.js
│
├── utils/           # 工具函数
│
├── App.vue          # 根组件
│
└── main.js          # 入口文件
```

## 数据库设计

### 实体关系图
```
   Season ──────┐
     │         │
     │         │
Tournament    Match ────── Event
     │         │           │
     │         │           │
     └───> Team <──────────┘
            │
            │
          Player
            │
            │
           User
```

### 数据表结构

1. **球员表（player）**
   - 球员ID (INT, PK)
   - 球员姓名 (VARCHAR)
   - 性别 (CHAR(1))
   - 球队ID (INT, FK -> team.球队ID)
   - 赛季ID (INT, FK -> season.赛季ID)
   - 赛季进球数 (INT)
   - 赛季红黄牌数 (INT)
   - 历史进球数 (INT)
   - 历史红黄牌数 (INT)

2. **球队表（team）**
   - 球队ID (INT, PK)
   - 球队名称 (VARCHAR)
   - 赛事ID (INT, FK -> tournament.赛事ID)
   - 赛季ID (INT, FK -> season.赛季ID)
   - 赛季总进球数 (INT)
   - 赛季红黄牌数 (INT)
   - 赛季积分 (INT)
   - 赛季排名 (INT)
   - 历史总进球数 (INT)
   - 历史总红黄牌数 (INT)

3. **比赛表（match）**
   - MatchID (INT, PK)
   - 比赛时间 (DATETIME)
   - 比赛地点 (VARCHAR)
   - 主队ID (INT, FK -> team.球队ID)
   - 客队ID (INT, FK -> team.球队ID)
   - 主队比分 (INT)
   - 客队比分 (INT)
   - 赛事ID (INT, FK -> tournament.赛事ID)
   - 赛季ID (INT, FK -> season.赛季ID)
   - 比赛状态 (CHAR(1))

4. **事件表（event）**
   - eventID (INT, PK)
   - MatchID (INT, FK -> match.MatchID)
   - 事件类型 (VARCHAR)
   - 球队ID (INT, FK -> team.球队ID)
   - 球员ID (INT, FK -> player.球员ID)
   - 赛季ID (INT, FK -> season.赛季ID)

5. **赛事表（tournament）**
   - 赛事ID (INT, PK)
   - 赛事名称 (VARCHAR)
   - 赛事类型 (VARCHAR)
   - 参赛单位类型 (VARCHAR)
   - 性别限制 (CHAR(1))

6. **赛季表（season）**
   - 赛季ID (INT, PK)
   - 赛季名称 (VARCHAR)
   - 赛季开始时间 (DATETIME)
   - 赛季结束时间 (DATETIME)

7. **用户表（user）**
   - 用户ID (INT, PK)
   - 用户名 (VARCHAR)
   - 用户密码 (VARCHAR)
   - 用户创建时间 (DATETIME)
   - 用户邮箱 (VARCHAR)
   - 用户身份 (VARCHAR)

## 主要功能

### 球员管理
- 球员信息的添加、修改、删除
- 查询球员信息
- 球员数据统计（进球、红黄牌等）

### 球队管理
- 球队信息的添加、修改、删除
- 查询球队信息
- 球队数据统计（积分、排名、进球等）

### 比赛管理
- 比赛信息的添加、修改、删除
- 比赛数据录入
- 比赛结果查询

### 事件管理
- 比赛事件的记录（进球、红黄牌等）
- 事件信息查询

### 赛事管理
- 赛事信息的添加、修改、删除
- 赛事查询

### 赛季管理
- 赛季信息的添加、修改、删除
- 赛季查询

### 用户管理
- 用户注册、登录、权限管理

### 数据统计与可视化
- 球员、球队数据统计
- 比赛数据分析
- 数据可视化展示

## 权限设计
- 管理员：拥有系统所有操作权限
- 普通用户：只能查看数据，无法修改
- 特定用户：可以修改特定数据（如比赛记录员）

## 开发与部署

### 开发环境
- JDK 11+
- Node.js 14+
- MySQL 8+
- Maven 3.6+
- IDE: IntelliJ IDEA, VS Code

### 部署要求
- 支持Docker容器化部署
- 数据库定期备份
- 日志系统

## 系统截图
[未来添加系统截图]

## 开发团队
[未来添加团队信息]

## 项目进度
[未来添加项目进度]

## 联系方式
[未来添加联系方式]