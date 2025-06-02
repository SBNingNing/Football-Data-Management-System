-- 创建数据库
CREATE DATABASE IF NOT EXISTS football_management_system;
USE football_management_system;

-- 创建赛季表(season)
CREATE TABLE season (
    赛季ID INT PRIMARY KEY AUTO_INCREMENT,
    赛季名称 VARCHAR(50) NOT NULL,
    赛季开始时间 DATETIME NOT NULL,
    赛季结束时间 DATETIME NOT NULL
);

-- 创建赛事表(tournament)
CREATE TABLE tournament (
    赛事ID INT PRIMARY KEY AUTO_INCREMENT,
    赛事名称 VARCHAR(100) NOT NULL,
    赛事类型 VARCHAR(50) NOT NULL,
    参赛单位类型 VARCHAR(50) NOT NULL,
    性别限制 CHAR(1) NOT NULL CHECK (性别限制 IN ('M', 'F', 'U'))
);

-- 创建球队表(team) - 修正字段名
CREATE TABLE team (
    球队ID INT PRIMARY KEY AUTO_INCREMENT,
    球队名称 VARCHAR(100) NOT NULL,
    赛事ID INT NOT NULL,
    赛季ID INT NOT NULL,
    赛季总进球数 INT DEFAULT 0,
    赛季红牌数 INT DEFAULT 0,
    赛季黄牌数 INT DEFAULT 0,
    赛季积分 INT DEFAULT 0,
    赛季排名 INT,
    历史总进球数 INT DEFAULT 0,
    历史总红牌数 INT DEFAULT 0,
    历史总黄牌数 INT DEFAULT 0,
    FOREIGN KEY (赛事ID) REFERENCES tournament(赛事ID),
    FOREIGN KEY (赛季ID) REFERENCES season(赛季ID)
);

-- 创建球员表(player)
CREATE TABLE player (
    球员ID INT PRIMARY KEY AUTO_INCREMENT,
    球员姓名 VARCHAR(50) NOT NULL,
    性别 CHAR(1) NOT NULL CHECK (性别 IN ('M', 'F')),
    球队ID INT NOT NULL,
    赛季ID INT NOT NULL,
    赛季进球数 INT DEFAULT 0,
    赛季红牌数 INT DEFAULT 0,
    赛季黄牌数 INT DEFAULT 0,
    历史进球数 INT DEFAULT 0,
    历史红牌数 INT DEFAULT 0,
    历史黄牌数 INT DEFAULT 0,
    FOREIGN KEY (球队ID) REFERENCES team(球队ID),
    FOREIGN KEY (赛季ID) REFERENCES season(赛季ID)
);

-- 创建比赛表(match)
CREATE TABLE `match` (
    MatchID INT PRIMARY KEY AUTO_INCREMENT,
    比赛时间 DATETIME NOT NULL,
    比赛地点 VARCHAR(100) NOT NULL,
    主队ID INT NOT NULL,
    客队ID INT NOT NULL,
    主队比分 INT DEFAULT 0,
    客队比分 INT DEFAULT 0,
    赛事ID INT NOT NULL,
    赛季ID INT NOT NULL,
    比赛状态 CHAR(1) NOT NULL CHECK (比赛状态 IN ('F', 'P')),
    FOREIGN KEY (主队ID) REFERENCES team(球队ID),
    FOREIGN KEY (客队ID) REFERENCES team(球队ID),
    FOREIGN KEY (赛事ID) REFERENCES tournament(赛事ID),
    FOREIGN KEY (赛季ID) REFERENCES season(赛季ID)
);

-- 创建事件表(event)
CREATE TABLE event (
    eventID INT PRIMARY KEY AUTO_INCREMENT,
    MatchID INT NOT NULL,
    事件类型 VARCHAR(50) NOT NULL,
    球队ID INT NOT NULL,
    球员ID INT NOT NULL,
    赛季ID INT NOT NULL,
    FOREIGN KEY (MatchID) REFERENCES `match`(MatchID),
    FOREIGN KEY (球队ID) REFERENCES team(球队ID),
    FOREIGN KEY (球员ID) REFERENCES player(球员ID),
    FOREIGN KEY (赛季ID) REFERENCES season(赛季ID)
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
-- 插入默认赛季
INSERT INTO season (赛季ID, 赛季名称, 赛季开始时间, 赛季结束时间) VALUES 
(1, '2024赛季', '2024-01-01 00:00:00', '2024-12-31 23:59:59');

-- 插入默认赛事
INSERT INTO tournament (赛事ID, 赛事名称, 赛事类型, 参赛单位类型, 性别限制) VALUES 
(1, '冠军杯', '淘汰赛', '学院', 'M'),
(2, '巾帼杯', '淘汰赛', '学院', 'F'),
(3, '八人制比赛', '循环赛', '学院', 'U');

-- 插入默认管理员用户
INSERT INTO user (用户名, 密码, 邮箱, 身份角色) VALUES 
('admin', 'scrypt:32768:8:1$hashed_password', 'admin@example.com', 'admin');
