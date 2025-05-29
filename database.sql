-- 创建数据库
CREATE DATABASE IF NOT EXISTS football_management;
USE football_management;

-- 创建赛季表
CREATE TABLE season (
    season_id INT PRIMARY KEY AUTO_INCREMENT,
    season_name VARCHAR(50) NOT NULL,
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建赛事表
CREATE TABLE tournament (
    tournament_id INT PRIMARY KEY AUTO_INCREMENT,
    tournament_name VARCHAR(100) NOT NULL,
    tournament_type VARCHAR(50) NOT NULL,
    participant_type VARCHAR(50) NOT NULL,
    gender_restriction CHAR(1) NOT NULL COMMENT 'M: 男，F: 女，U: 不限'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建球队表
CREATE TABLE team (
    team_id INT PRIMARY KEY AUTO_INCREMENT,
    team_name VARCHAR(100) NOT NULL,
    tournament_id INT NOT NULL,
    season_id INT NOT NULL,
    season_goals INT DEFAULT 0,
    season_cards INT DEFAULT 0,
    season_points INT DEFAULT 0,
    season_rank INT,
    historical_goals INT DEFAULT 0,
    historical_cards INT DEFAULT 0,
    FOREIGN KEY (tournament_id) REFERENCES tournament(tournament_id),
    FOREIGN KEY (season_id) REFERENCES season(season_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建球员表
CREATE TABLE player (
    player_id INT PRIMARY KEY AUTO_INCREMENT,
    player_name VARCHAR(100) NOT NULL,
    gender CHAR(1) NOT NULL COMMENT 'M: 男，F: 女',
    team_id INT NOT NULL,
    season_id INT NOT NULL,
    season_goals INT DEFAULT 0,
    season_cards INT DEFAULT 0,
    historical_goals INT DEFAULT 0,
    historical_cards INT DEFAULT 0,
    FOREIGN KEY (team_id) REFERENCES team(team_id),
    FOREIGN KEY (season_id) REFERENCES season(season_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建比赛表
CREATE TABLE `match` (
    match_id INT PRIMARY KEY AUTO_INCREMENT,
    match_time DATETIME NOT NULL,
    match_location VARCHAR(100) NOT NULL,
    home_team_id INT NOT NULL,
    away_team_id INT NOT NULL,
    home_score INT DEFAULT 0,
    away_score INT DEFAULT 0,
    tournament_id INT NOT NULL,
    season_id INT NOT NULL,
    match_status CHAR(1) NOT NULL DEFAULT 'P' COMMENT 'F: 已结束，P: 未结束',
    FOREIGN KEY (home_team_id) REFERENCES team(team_id),
    FOREIGN KEY (away_team_id) REFERENCES team(team_id),
    FOREIGN KEY (tournament_id) REFERENCES tournament(tournament_id),
    FOREIGN KEY (season_id) REFERENCES season(season_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建事件表
CREATE TABLE event (
    event_id INT PRIMARY KEY AUTO_INCREMENT,
    match_id INT NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    team_id INT NOT NULL,
    player_id INT NOT NULL,
    season_id INT NOT NULL,
    event_time DATETIME NOT NULL,
    FOREIGN KEY (match_id) REFERENCES `match`(match_id),
    FOREIGN KEY (team_id) REFERENCES team(team_id),
    FOREIGN KEY (player_id) REFERENCES player(player_id),
    FOREIGN KEY (season_id) REFERENCES season(season_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建用户表
CREATE TABLE user (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    email VARCHAR(100),
    user_type VARCHAR(20) NOT NULL COMMENT '球队队员、管理员、游客'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 添加索引
ALTER TABLE player ADD INDEX idx_player_team (team_id);
ALTER TABLE player ADD INDEX idx_player_season (season_id);
ALTER TABLE team ADD INDEX idx_team_tournament (tournament_id);
ALTER TABLE team ADD INDEX idx_team_season (season_id);
ALTER TABLE `match` ADD INDEX idx_match_tournament (tournament_id);
ALTER TABLE `match` ADD INDEX idx_match_season (season_id);
ALTER TABLE event ADD INDEX idx_event_match (match_id);
ALTER TABLE event ADD INDEX idx_event_player (player_id);
