# 足球赛事管理系统数据库设计

## 数据库概述

本数据库设计用于支持科大校园足球赛事管理系统，存储和管理与足球赛事相关的各类数据。

## 实体关系图

![数据库ER图](./images/database_er.png)

## 数据表设计

### 1. 球员表 (player)

| 列名             | 数据类型     | 约束                    | 描述                     |
|-----------------|-------------|------------------------|--------------------------|
| player_id       | INT         | PRIMARY KEY, AUTO_INCREMENT | 球员的唯一标识           |
| player_name     | VARCHAR(50) | NOT NULL               | 球员的姓名               |
| gender          | CHAR(1)     | NOT NULL, CHECK (gender IN ('M', 'F')) | 球员的性别（M/F）  |
| team_id         | INT         | FOREIGN KEY            | 球员所属球队的ID         |
| season_id       | INT         | FOREIGN KEY            | 球员所属赛季的ID         |
| season_goals    | INT         | DEFAULT 0              | 球员在当前赛季的进球数   |
| season_cards    | INT         | DEFAULT 0              | 球员在当前赛季的红黄牌数 |
| historical_goals| INT         | DEFAULT 0              | 球员历史总进球数         |
| historical_cards| INT         | DEFAULT 0              | 球员历史总红黄牌数       |
| created_at      | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP | 创建时间                 |
| updated_at      | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

**索引：**
- 主键索引：`player_id`
- 外键索引：`team_id`, `season_id`
- 普通索引：`player_name`

### 2. 球队表 (team)

| 列名               | 数据类型     | 约束                    | 描述                     |
|-------------------|-------------|------------------------|--------------------------|
| team_id           | INT         | PRIMARY KEY, AUTO_INCREMENT | 球队的唯一标识           |
| team_name         | VARCHAR(50) | NOT NULL               | 球队的名称               |
| tournament_id     | INT         | FOREIGN KEY            | 球队参加的赛事ID         |
| season_id         | INT         | FOREIGN KEY            | 球队参加的赛季ID         |
| season_goals      | INT         | DEFAULT 0              | 球队在当前赛季的总进球数 |
| season_cards      | INT         | DEFAULT 0              | 球队在当前赛季的红黄牌数 |
| season_points     | INT         | DEFAULT 0              | 球队在当前赛季的积分     |
| season_rank       | INT         | DEFAULT 0              | 球队在当前赛季的排名     |
| historical_goals  | INT         | DEFAULT 0              | 球队历史总进球数         |
| historical_cards  | INT         | DEFAULT 0              | 球队历史总红黄牌数       |
| created_at        | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP | 创建时间                 |
| updated_at        | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

**索引：**
- 主键索引：`team_id`
- 外键索引：`tournament_id`, `season_id`
- 普通索引：`team_name`

### 3. 比赛表 (match)

| 列名         | 数据类型     | 约束                    | 描述                             |
|-------------|-------------|------------------------|----------------------------------|
| match_id    | INT         | PRIMARY KEY, AUTO_INCREMENT | 比赛的唯一标识                   |
| match_time  | DATETIME    | NOT NULL               | 比赛的时间                       |
| location    | VARCHAR(100)| NOT NULL               | 比赛的地点                       |
| home_team_id| INT         | FOREIGN KEY            | 主队的球队ID                     |
| away_team_id| INT         | FOREIGN KEY            | 客队的球队ID                     |
| home_score  | INT         | DEFAULT 0              | 主队的比分                       |
| away_score  | INT         | DEFAULT 0              | 客队的比分                       |
| tournament_id| INT        | FOREIGN KEY            | 比赛所属的赛事ID                 |
| season_id   | INT         | FOREIGN KEY            | 比赛所属的赛季ID                 |
| match_status| CHAR(1)     | NOT NULL, DEFAULT 'P', CHECK (match_status IN ('F', 'P')) | 比赛状态（F: 已结束，P: 未结束） |
| created_at  | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP | 创建时间                         |
| updated_at  | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

**索引：**
- 主键索引：`match_id`
- 外键索引：`home_team_id`, `away_team_id`, `tournament_id`, `season_id`
- 普通索引：`match_time`, `match_status`

### 4. 事件表 (event)

| 列名         | 数据类型     | 约束                    | 描述                         |
|-------------|-------------|------------------------|------------------------------|
| event_id    | INT         | PRIMARY KEY, AUTO_INCREMENT | 事件的唯一标识               |
| match_id    | INT         | FOREIGN KEY            | 事件所属的比赛ID             |
| event_type  | VARCHAR(20) | NOT NULL               | 事件的类型（如进球、红牌等） |
| team_id     | INT         | FOREIGN KEY            | 事件涉及的球队ID             |
| player_id   | INT         | FOREIGN KEY            | 事件涉及的球员ID             |
| season_id   | INT         | FOREIGN KEY            | 事件所属的赛季ID             |
| event_time  | INT         | NOT NULL               | 事件发生的比赛时间（分钟）   |
| description | VARCHAR(255)| NULL                   | 事件描述                     |
| created_at  | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP | 创建时间                     |
| updated_at  | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

**索引：**
- 主键索引：`event_id`
- 外键索引：`match_id`, `team_id`, `player_id`, `season_id`
- 普通索引：`event_type`

### 5. 赛事表 (tournament)

| 列名             | 数据类型     | 约束                    | 描述                              |
|-----------------|-------------|------------------------|-----------------------------------|
| tournament_id   | INT         | PRIMARY KEY, AUTO_INCREMENT | 赛事的唯一标识                    |
| tournament_name | VARCHAR(50) | NOT NULL               | 赛事的名称（如冠军杯、巾帼杯等）  |
| tournament_type | VARCHAR(20) | NOT NULL               | 赛事的类型（如11人制、8人制等）   |
| entity_type     | VARCHAR(20) | NOT NULL               | 参赛单位类型（如学院、俱乐部等）  |
| gender_limit    | CHAR(1)     | NOT NULL, CHECK (gender_limit IN ('M', 'F', 'U')) | 性别限制（M: 男，F: 女，U: 不限） |
| created_at      | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP | 创建时间                          |
| updated_at      | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

**索引：**
- 主键索引：`tournament_id`
- 普通索引：`tournament_name`, `tournament_type`

### 6. 赛季表 (season)

| 列名         | 数据类型     | 约束                    | 描述                     |
|-------------|-------------|------------------------|--------------------------|
| season_id   | INT         | PRIMARY KEY, AUTO_INCREMENT | 赛季的唯一标识           |
| season_name | VARCHAR(50) | NOT NULL               | 赛季的名称（如2023赛季） |
| start_date  | DATE        | NOT NULL               | 赛季的开始时间           |
| end_date    | DATE        | NOT NULL               | 赛季的结束时间           |
| created_at  | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP | 创建时间                 |
| updated_at  | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

**索引：**
- 主键索引：`season_id`
- 普通索引：`season_name`, `start_date`, `end_date`

### 7. 用户表 (user)

| 列名         | 数据类型     | 约束                    | 描述                     |
|-------------|-------------|------------------------|--------------------------|
| user_id     | INT         | PRIMARY KEY, AUTO_INCREMENT | 用户的唯一标识           |
| username    | VARCHAR(50) | NOT NULL, UNIQUE       | 用户名                   |
| password    | VARCHAR(255)| NOT NULL               | 密码（加密存储）         |
| real_name   | VARCHAR(50) | NULL                   | 真实姓名                 |
| email       | VARCHAR(100)| NULL, UNIQUE           | 电子邮件                 |
| phone       | VARCHAR(20) | NULL                   | 电话号码                 |
| role_id     | INT         | FOREIGN KEY            | 用户角色ID               |
| status      | TINYINT     | NOT NULL, DEFAULT 1    | 用户状态（1:启用, 0:禁用）|
| created_at  | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP | 创建时间                 |
| updated_at  | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

**索引：**
- 主键索引：`user_id`
- 唯一索引：`username`, `email`
- 外键索引：`role_id`

### 8. 角色表 (role)

| 列名         | 数据类型     | 约束                    | 描述                     |
|-------------|-------------|------------------------|--------------------------|
| role_id     | INT         | PRIMARY KEY, AUTO_INCREMENT | 角色的唯一标识           |
| role_name   | VARCHAR(50) | NOT NULL, UNIQUE       | 角色名称                 |
| description | VARCHAR(255)| NULL                   | 角色描述                 |
| created_at  | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP | 创建时间                 |
| updated_at  | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

**索引：**
- 主键索引：`role_id`
- 唯一索引：`role_name`

## 表关系

1. **球员表与球队表**：多对一关系，一个球队有多个球员，一个球员属于一个球队
2. **球队表与赛事表**：多对一关系，一个赛事有多个球队参加
3. **球队表与赛季表**：多对一关系，一个赛季有多个球队参加
4. **比赛表与球队表**：两个多对一关系（主队和客队）
5. **比赛表与赛事表**：多对一关系，一个赛事包含多个比赛
6. **比赛表与赛季表**：多对一关系，一个赛季包含多个比赛
7. **事件表与比赛表**：多对一关系，一个比赛有多个事件
8. **事件表与球队表**：多对一关系，一个事件关联一个球队
9. **事件表与球员表**：多对一关系，一个事件关联一个球员
10. **用户表与角色表**：多对一关系，一个角色可以分配给多个用户

## 数据库约束

### 主键约束
每张表都有其唯一标识的主键，如球员表的`player_id`、球队表的`team_id`等。

### 外键约束
表之间的关系通过外键进行约束，确保数据的一致性和完整性。

### 唯一性约束
某些字段需要保持唯一性，如用户表的`username`和`email`。

### CHECK约束
对某些字段的值进行限制，如性别字段只能是'M'或'F'。

## 索引设计

除了主键和外键索引外，还为经常用于查询和排序的字段创建了普通索引，以提高查询性能。

## 触发器设计

可以设计以下触发器来自动维护某些数据：

1. **比赛结束后更新球队积分**：当比赛状态从'P'变为'F'时，自动更新相关球队的积分。
2. **记录进球事件后更新球员和球队的进球数**：当新增进球类型的事件记录时，自动更新相关球员和球队的进球数。
3. **记录红黄牌事件后更新球员和球队的红黄牌数**：当新增红黄牌类型的事件记录时，自动更新相关球员和球队的红黄牌数。

## 数据字典

详细的字段说明、约束和验证规则可以在实际开发过程中进一步细化和完善。
