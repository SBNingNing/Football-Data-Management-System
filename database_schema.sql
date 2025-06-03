-- 创建数据库
CREATE DATABASE IF NOT EXISTS football_management_system;
USE football_management_system;

-- 创建合并后的赛事表(tournament)
CREATE TABLE tournament (
    赛事ID INT PRIMARY KEY AUTO_INCREMENT,
    赛事名称 VARCHAR(100) NOT NULL,
    赛事类型 VARCHAR(50) NOT NULL,
    性别限制 CHAR(1) NOT NULL CHECK (性别限制 IN ('M', 'F', 'U')),
    赛季名称 VARCHAR(50) NOT NULL,
    赛季开始时间 DATETIME NOT NULL,
    赛季结束时间 DATETIME NOT NULL
);

-- 创建球队表(team) 
CREATE TABLE team (
    球队ID INT PRIMARY KEY AUTO_INCREMENT,
    球队名称 VARCHAR(100) NOT NULL,
    赛事ID INT NOT NULL,
    赛季总进球数 INT DEFAULT 0,
    赛季红牌数 INT DEFAULT 0,
    赛季黄牌数 INT DEFAULT 0,
    赛季积分 INT DEFAULT 0,
    赛季排名 INT,
    FOREIGN KEY (赛事ID) REFERENCES tournament(赛事ID)
);

-- 创建球员表(player) - 修改为支持一对多关系，使用学号作为主键
CREATE TABLE player (
     球员ID VARCHAR(20) PRIMARY KEY,
    球员姓名 VARCHAR(50) NOT NULL,
    性别 CHAR(1) NOT NULL CHECK (性别 IN ('M', 'F')),
    当前球队ID INT,
    职业生涯总进球数 INT DEFAULT 0,
    职业生涯总红牌数 INT DEFAULT 0,
    职业生涯总黄牌数 INT DEFAULT 0,
    注册时间 DATETIME DEFAULT CURRENT_TIMESTAMP,
    状态 CHAR(1) DEFAULT 'A' CHECK (状态 IN ('A', 'I', 'R')), -- A:激活 I:非激活 R:退役
    FOREIGN KEY (当前球队ID) REFERENCES team(球队ID)
);

-- 创建球员转会记录表(player_team_history) - 优化支持多球队同时效力
CREATE TABLE player_team_history (
    记录ID INT PRIMARY KEY AUTO_INCREMENT,
    球员ID VARCHAR(20) NOT NULL,
    球队ID INT NOT NULL,
    赛事ID INT NOT NULL,
    加入时间 DATETIME NOT NULL,
    离开时间 DATETIME,
    赛季进球数 INT DEFAULT 0,
    赛季红牌数 INT DEFAULT 0,
    赛季黄牌数 INT DEFAULT 0,
    状态 CHAR(1) DEFAULT 'A' CHECK (状态 IN ('A', 'T', 'L')), -- A:当前激活 T:已转会 L:租借
    备注 TEXT,
    FOREIGN KEY (球员ID) REFERENCES player(球员ID),
    FOREIGN KEY (球队ID) REFERENCES team(球队ID),
    FOREIGN KEY (赛事ID) REFERENCES tournament(赛事ID),
    -- 确保同一球员在同一赛事中的同一球队不能有重复的激活记录
    UNIQUE KEY unique_active_player_team_tournament (球员ID, 球队ID, 赛事ID, 状态),
    -- 添加索引提高查询性能
    INDEX idx_player_active (球员ID, 状态),
    INDEX idx_team_tournament (球队ID, 赛事ID)
);

-- 创建比赛表(match) - 添加淘汰赛轮次信息
CREATE TABLE `match` (
    MatchID INT PRIMARY KEY AUTO_INCREMENT,
    比赛时间 DATETIME NOT NULL,
    比赛地点 VARCHAR(100) NOT NULL,
    主队ID INT NOT NULL,
    客队ID INT NOT NULL,
    主队比分 INT DEFAULT 0,
    客队比分 INT DEFAULT 0,
    赛事ID INT NOT NULL,
    比赛状态 CHAR(1) NOT NULL CHECK (比赛状态 IN ('F', 'P')),
    比赛类型 VARCHAR(20) DEFAULT '常规赛' CHECK (比赛类型 IN ('常规赛', '淘汰赛')),
    淘汰赛轮次 INT, -- 1:1/8决赛, 2:1/4决赛, 3:半决赛, 4:决赛
    FOREIGN KEY (主队ID) REFERENCES team(球队ID),
    FOREIGN KEY (客队ID) REFERENCES team(球队ID),
    FOREIGN KEY (赛事ID) REFERENCES tournament(赛事ID)
);

-- 创建事件表(event) 
CREATE TABLE event (
    eventID INT PRIMARY KEY AUTO_INCREMENT,
    MatchID INT NOT NULL,
    事件类型 VARCHAR(50) NOT NULL,
    球队ID INT NOT NULL,
    球员ID VARCHAR(20) NOT NULL,
    FOREIGN KEY (MatchID) REFERENCES `match`(MatchID),
    FOREIGN KEY (球队ID) REFERENCES team(球队ID),
    FOREIGN KEY (球员ID) REFERENCES player(球员ID)
);

-- 创建用户表(user)
CREATE TABLE user (
    用户ID INT PRIMARY KEY AUTO_INCREMENT,
    用户名 VARCHAR(50) NOT NULL UNIQUE,
    密码 VARCHAR(255) NOT NULL,
    邮箱 VARCHAR(100) NOT NULL UNIQUE,
    身份角色 VARCHAR(20) NOT NULL DEFAULT 'user',
    创建时间 DATETIME DEFAULT CURRENT_TIMESTAMP,
    最后登录时间 DATETIME,
    状态 CHAR(1) DEFAULT 'A' CHECK (状态 IN ('A', 'D'))
);

-- 插入默认数据
-- 插入默认赛事
INSERT INTO tournament (赛事ID, 赛事名称, 赛事类型, 性别限制, 赛季名称, 赛季开始时间, 赛季结束时间) VALUES 
(1, '冠军杯', '常规赛', 'M', '2024赛季', '2024-01-01 00:00:00', '2024-12-31 23:59:59'),
(2, '巾帼杯', '常规赛', 'F', '2024赛季', '2024-01-01 00:00:00', '2024-12-31 23:59:59'),
(3, '八人制比赛', '常规赛','U', '2024赛季', '2024-01-01 00:00:00', '2024-12-31 23:59:59');

-- 插入默认管理员用户
INSERT INTO user (用户名, 密码, 邮箱, 身份角色) VALUES 
('admin', 'scrypt:32768:8:1$hashed_password', 'admin@example.com', 'admin');
