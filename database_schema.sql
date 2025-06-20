-- 创建数据库
CREATE DATABASE IF NOT EXISTS football_management_system;
USE football_management_system;



-- 创建合并后的赛事表(tournament)，不同赛季的同种赛事也具有不同id
CREATE TABLE tournament (
    赛事ID INT PRIMARY KEY AUTO_INCREMENT,
    赛事名称 VARCHAR(100) NOT NULL,-- 如冠军杯
    赛季名称 VARCHAR(50) NOT NULL,
    常规赛是否分组 BOOLEAN DEFAULT FALSE COMMENT '常规赛是否需要分组进行',
    赛季开始时间 DATETIME NOT NULL,
    赛季结束时间 DATETIME NOT NULL
);

-- 创建球队表(team) 
CREATE TABLE team (
    球队ID INT PRIMARY KEY AUTO_INCREMENT,
    球队名称 VARCHAR(100) NOT NULL,
    小组ID CHAR(1) NULL,
    赛事ID INT NOT NULL,
    赛事总进球数 INT DEFAULT 0 CHECK (赛事总进球数 >= 0),
    赛事总失球数量 INT DEFAULT 0 CHECK (赛事总失球数量 >= 0),
    赛事总净胜球 INT DEFAULT 0,
    赛事红牌数 INT DEFAULT 0 CHECK (赛事红牌数 >= 0),
    赛事黄牌数 INT DEFAULT 0 CHECK (赛事黄牌数 >= 0),
    赛事积分 INT DEFAULT 0 CHECK (赛事积分 >= 0),
    赛事排名 INT CHECK (赛事排名 > 0),
    CONSTRAINT fk_team_tournament FOREIGN KEY (赛事ID) REFERENCES tournament(赛事ID) ON DELETE CASCADE,
    INDEX idx_team_tournament (赛事ID)
);

-- 创建球员表(player) - 修改为支持一对多关系，使用学号作为主键
CREATE TABLE player (
    球员ID VARCHAR(20) PRIMARY KEY,
    球员姓名 VARCHAR(50) NOT NULL,
    职业生涯总进球数 INT DEFAULT 0 CHECK (职业生涯总进球数 >= 0),
    职业生涯总红牌数 INT DEFAULT 0 CHECK (职业生涯总红牌数 >= 0),
    职业生涯总黄牌数 INT DEFAULT 0 CHECK (职业生涯总黄牌数 >= 0)
);

-- 创建球员-队伍记录表(player_team_history) 
CREATE TABLE player_team_history (
    记录ID INT PRIMARY KEY AUTO_INCREMENT,
    球员ID VARCHAR(20) NOT NULL,
    球员号码 INT NOT NULL,
    球队ID INT NULL, -- 修改为允许 NULL
    赛事ID INT NOT NULL,
    赛事进球数 INT DEFAULT 0 CHECK (赛事进球数 >= 0),
    赛事红牌数 INT DEFAULT 0 CHECK (赛事红牌数 >= 0),
    赛事黄牌数 INT DEFAULT 0 CHECK (赛事黄牌数 >= 0),
    备注 TEXT,
    CONSTRAINT fk_pth_player FOREIGN KEY (球员ID) REFERENCES player(球员ID) ON DELETE CASCADE,
    CONSTRAINT fk_pth_team FOREIGN KEY (球队ID) REFERENCES team(球队ID) ON DELETE CASCADE,
    CONSTRAINT fk_pth_tournament FOREIGN KEY (赛事ID) REFERENCES tournament(赛事ID) ON DELETE CASCADE,
    UNIQUE KEY unique_active_player_team_tournament (球员ID, 球队ID, 赛事ID),
    INDEX idx_team_tournament (球队ID, 赛事ID),
    INDEX idx_player_tournament (球员ID, 赛事ID)
);

-- 创建比赛表(match) - 添加淘汰赛轮次信息
CREATE TABLE `match` (
    MatchID VARCHAR(50) PRIMARY KEY, 
    比赛名称 VARCHAR(50) NOT NULL,
    赛事ID INT NOT NULL,
    小组ID CHAR(1) NULL,
    比赛时间 DATETIME NOT NULL,
    比赛地点 VARCHAR(50) NOT NULL,
    主队ID INT NULL, -- 修改为允许 NULL
    客队ID INT NULL, -- 修改为允许 NULL
    主队比分 INT DEFAULT 0,
    客队比分 INT DEFAULT 0,
    比赛状态 CHAR(1) NOT NULL CHECK (比赛状态 IN ('F', 'P')),
    淘汰赛轮次 INT, -- 0:常规赛, 1:附加赛, 2:1/4决赛, 3:半决赛, 4:决赛
    CONSTRAINT fk_match_home_team FOREIGN KEY (主队ID) REFERENCES team(球队ID) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_match_away_team FOREIGN KEY (客队ID) REFERENCES team(球队ID) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_match_tournament FOREIGN KEY (赛事ID) REFERENCES tournament(赛事ID) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_match_home_team (主队ID),
    INDEX idx_match_away_team (客队ID),
    INDEX idx_match_tournament (赛事ID),
    INDEX idx_match_time (比赛时间),
    INDEX idx_match_status (比赛状态)
);

-- 创建事件表(event) - 确保所有外键都有级联删除
CREATE TABLE event (
    eventID INT PRIMARY KEY AUTO_INCREMENT,
    MatchID VARCHAR(50) NOT NULL,
    事件类型 VARCHAR(50) NOT NULL,
    球队ID INT NULL, -- 修改为允许 NULL
    球员ID VARCHAR(20) NOT NULL,
    事件时间 INT NULL COMMENT '事件发生时间（比赛第几分钟）',
    CONSTRAINT fk_event_match FOREIGN KEY (MatchID) REFERENCES `match`(MatchID) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_event_team FOREIGN KEY (球队ID) REFERENCES team(球队ID) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_event_player FOREIGN KEY (球员ID) REFERENCES player(球员ID) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_event_match (MatchID),
    INDEX idx_event_team (球队ID),
    INDEX idx_event_player (球员ID),
    INDEX idx_event_type (事件类型)
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
INSERT INTO tournament (赛事ID, 赛事名称, 赛季名称, 赛季开始时间, 赛季结束时间) VALUES 
(1, '冠军杯','2024赛季', '2024-01-01 00:00:00', '2024-12-31 23:59:59'),
(2, '巾帼杯', '2024赛季', '2024-01-01 00:00:00', '2024-12-31 23:59:59'),
(3, '八人制比赛', '2024赛季', '2024-01-01 00:00:00', '2024-12-31 23:59:59');

-- 插入默认管理员用户
INSERT INTO user (用户名, 密码, 邮箱, 身份角色) VALUES 
('admin', 'scrypt:32768:8:1$hashed_password', 'admin@example.com', 'admin');

-- 验证级联删除设置（可选）
SHOW CREATE TABLE team;
SHOW CREATE TABLE player_team_history;
SHOW CREATE TABLE `match`;
SHOW CREATE TABLE event;

