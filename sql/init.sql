-- 足球赛事管理系统数据库初始化脚本

-- 创建数据库
CREATE DATABASE IF NOT EXISTS football_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE football_management;

-- 创建赛事表
CREATE TABLE tournament (
    tournament_id INT AUTO_INCREMENT PRIMARY KEY,
    tournament_name VARCHAR(50) NOT NULL,
    tournament_type VARCHAR(20) NOT NULL,
    entity_type VARCHAR(20) NOT NULL,
    gender_limit CHAR(1) NOT NULL CHECK (gender_limit IN ('M', 'F', 'U')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_tournament_name (tournament_name),
    INDEX idx_tournament_type (tournament_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建赛季表
CREATE TABLE season (
    season_id INT AUTO_INCREMENT PRIMARY KEY,
    season_name VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_season_name (season_name),
    INDEX idx_date (start_date, end_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建球队表
CREATE TABLE team (
    team_id INT AUTO_INCREMENT PRIMARY KEY,
    team_name VARCHAR(50) NOT NULL,
    tournament_id INT NOT NULL,
    season_id INT NOT NULL,
    season_goals INT DEFAULT 0,
    season_cards INT DEFAULT 0,
    season_points INT DEFAULT 0,
    season_rank INT DEFAULT 0,
    historical_goals INT DEFAULT 0,
    historical_cards INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (tournament_id) REFERENCES tournament (tournament_id),
    FOREIGN KEY (season_id) REFERENCES season (season_id),
    INDEX idx_team_name (team_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建球员表
CREATE TABLE player (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    player_name VARCHAR(50) NOT NULL,
    gender CHAR(1) NOT NULL CHECK (gender IN ('M', 'F')),
    team_id INT NOT NULL,
    season_id INT NOT NULL,
    season_goals INT DEFAULT 0,
    season_cards INT DEFAULT 0,
    historical_goals INT DEFAULT 0,
    historical_cards INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES team (team_id),
    FOREIGN KEY (season_id) REFERENCES season (season_id),
    INDEX idx_player_name (player_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建比赛表
CREATE TABLE `match` (
    match_id INT AUTO_INCREMENT PRIMARY KEY,
    match_time DATETIME NOT NULL,
    location VARCHAR(100) NOT NULL,
    home_team_id INT NOT NULL,
    away_team_id INT NOT NULL,
    home_score INT DEFAULT 0,
    away_score INT DEFAULT 0,
    tournament_id INT NOT NULL,
    season_id INT NOT NULL,
    match_status CHAR(1) NOT NULL DEFAULT 'P' CHECK (match_status IN ('F', 'P')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (home_team_id) REFERENCES team (team_id),
    FOREIGN KEY (away_team_id) REFERENCES team (team_id),
    FOREIGN KEY (tournament_id) REFERENCES tournament (tournament_id),
    FOREIGN KEY (season_id) REFERENCES season (season_id),
    INDEX idx_match_time (match_time),
    INDEX idx_match_status (match_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建事件表
CREATE TABLE event (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    match_id INT NOT NULL,
    event_type VARCHAR(20) NOT NULL,
    team_id INT NOT NULL,
    player_id INT NOT NULL,
    season_id INT NOT NULL,
    event_time INT NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id) REFERENCES `match` (match_id),
    FOREIGN KEY (team_id) REFERENCES team (team_id),
    FOREIGN KEY (player_id) REFERENCES player (player_id),
    FOREIGN KEY (season_id) REFERENCES season (season_id),
    INDEX idx_event_type (event_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建角色表
CREATE TABLE role (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建用户表
CREATE TABLE user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    real_name VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    role_id INT NOT NULL,
    status TINYINT NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES role (role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入基础角色数据
INSERT INTO role (role_name, description) VALUES 
('admin', '系统管理员'),
('recorder', '赛事记录员'),
('guest', '游客');

-- 插入默认管理员账号（密码需要在实际使用时修改）
-- 密码为admin123的MD5加密值，实际使用时应采用更安全的加密方式
INSERT INTO user (username, password, real_name, role_id) VALUES 
('admin', '0192023a7bbd73250516f069df18b500', '系统管理员', 1);

-- 创建触发器：比赛结束后更新球队积分
DELIMITER //
CREATE TRIGGER after_match_finished
AFTER UPDATE ON `match`
FOR EACH ROW
BEGIN
    IF NEW.match_status = 'F' AND OLD.match_status = 'P' THEN
        -- 主队获胜
        IF NEW.home_score > NEW.away_score THEN
            UPDATE team SET season_points = season_points + 3 WHERE team_id = NEW.home_team_id;
        -- 客队获胜
        ELSEIF NEW.away_score > NEW.home_score THEN
            UPDATE team SET season_points = season_points + 3 WHERE team_id = NEW.away_team_id;
        -- 平局
        ELSE
            UPDATE team SET season_points = season_points + 1 WHERE team_id IN (NEW.home_team_id, NEW.away_team_id);
        END IF;
        
        -- 更新球队进球数
        UPDATE team SET season_goals = season_goals + NEW.home_score WHERE team_id = NEW.home_team_id;
        UPDATE team SET season_goals = season_goals + NEW.away_score WHERE team_id = NEW.away_team_id;
    END IF;
END //
DELIMITER ;

-- 创建触发器：记录进球事件后更新球员和球队的进球数
DELIMITER //
CREATE TRIGGER after_goal_event
AFTER INSERT ON event
FOR EACH ROW
BEGIN
    IF NEW.event_type = 'GOAL' THEN
        -- 更新球员进球数
        UPDATE player 
        SET 
            season_goals = season_goals + 1,
            historical_goals = historical_goals + 1
        WHERE player_id = NEW.player_id;
    END IF;
END //
DELIMITER ;

-- 创建触发器：记录红黄牌事件后更新球员和球队的红黄牌数
DELIMITER //
CREATE TRIGGER after_card_event
AFTER INSERT ON event
FOR EACH ROW
BEGIN
    IF NEW.event_type IN ('YELLOW_CARD', 'RED_CARD') THEN
        -- 更新球员红黄牌数
        UPDATE player 
        SET 
            season_cards = season_cards + 1,
            historical_cards = historical_cards + 1
        WHERE player_id = NEW.player_id;
        
        -- 更新球队红黄牌数
        UPDATE team 
        SET 
            season_cards = season_cards + 1,
            historical_cards = historical_cards + 1
        WHERE team_id = NEW.team_id;
    END IF;
END //
DELIMITER ;
