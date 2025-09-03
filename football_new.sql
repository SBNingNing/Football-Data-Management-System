CREATE DATABASE IF NOT EXISTS `football_management_system` /*!40100 DEFAULT CHARACTER SET utf8mb3 */;
USE `football_management_system`;

-- =============================
-- 赛事表 (competition)
-- =============================
DROP TABLE IF EXISTS `competition`;
CREATE TABLE `competition` (
  `competition_id` INT NOT NULL AUTO_INCREMENT,
  `赛事名称` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`competition_id`),
  UNIQUE KEY (`赛事名称`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- =============================
-- 赛季表 (season)
-- =============================
DROP TABLE IF EXISTS `season`;
CREATE TABLE `season` (
  `season_id` INT NOT NULL AUTO_INCREMENT,
  `赛季名称` VARCHAR(50) NOT NULL,
  `开始时间` DATETIME NOT NULL,
  `结束时间` DATETIME NOT NULL,
  PRIMARY KEY (`season_id`),
  UNIQUE KEY (`赛季名称`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- =============================
-- 赛事-赛季实例表 (tournament)
-- =============================
DROP TABLE IF EXISTS `tournament`;
CREATE TABLE `tournament` (
  `赛事ID` INT NOT NULL AUTO_INCREMENT,
  `competition_id` INT NOT NULL,
  `season_id` INT NOT NULL,
  `常规赛是否分组` TINYINT(1) DEFAULT '0',
  `常规赛小组数` TINYINT UNSIGNED DEFAULT NULL,
  `淘汰赛名额数` TINYINT UNSIGNED DEFAULT NULL,
  PRIMARY KEY (`赛事ID`),
  KEY `idx_tournament_competition` (`competition_id`),
  KEY `idx_tournament_season` (`season_id`),
  CONSTRAINT `fk_tournament_competition` FOREIGN KEY (`competition_id`) REFERENCES `competition` (`competition_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_tournament_season` FOREIGN KEY (`season_id`) REFERENCES `season` (`season_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- =============================
-- 球队基础信息表 (team_base)
-- =============================
DROP TABLE IF EXISTS `team_base`;
CREATE TABLE `team_base` (
  `球队基础ID` INT NOT NULL AUTO_INCREMENT,
  `球队名称` VARCHAR(100) NOT NULL,
  `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `备注` TEXT DEFAULT NULL,
  PRIMARY KEY (`球队基础ID`),
  UNIQUE KEY `uk_team_name` (`球队名称`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb3;

-- =============================
-- 球队赛事参与表 (team_tournament_participation)
-- 记录球队在特定赛事中的表现
-- =============================
DROP TABLE IF EXISTS `team_tournament_participation`;
CREATE TABLE `team_tournament_participation` (
  `参与ID` INT NOT NULL AUTO_INCREMENT,
  `球队基础ID` INT NOT NULL,
  `赛事ID` INT NOT NULL,
  `小组ID` CHAR(1) DEFAULT NULL,
  -- 赛事统计数据
  `赛事总进球数` INT DEFAULT 0,
  `赛事总失球数量` INT DEFAULT 0,
  `赛事总净胜球` INT DEFAULT 0,
  `赛事红牌数` INT DEFAULT 0,
  `赛事黄牌数` INT DEFAULT 0,
  `赛事积分` INT DEFAULT 0,
  `赛事排名` INT DEFAULT NULL,
  -- 比赛记录统计
  `比赛轮数` INT NOT NULL DEFAULT 0,
  `胜场数` INT NOT NULL DEFAULT 0,
  `平场数` INT NOT NULL DEFAULT 0,
  `负场数` INT NOT NULL DEFAULT 0,
  -- 参与时间记录
  `报名时间` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `状态` ENUM('active', 'withdrawn', 'completed') DEFAULT 'active',
  
  PRIMARY KEY (`参与ID`),
  UNIQUE KEY `uk_team_tournament` (`球队基础ID`, `赛事ID`),
  KEY `idx_team_base` (`球队基础ID`),
  KEY `idx_tournament` (`赛事ID`),
  KEY `idx_team_tournament_status` (`球队基础ID`, `赛事ID`, `状态`),
  
  CONSTRAINT `fk_ttp_team_base` 
      FOREIGN KEY (`球队基础ID`) REFERENCES `team_base` (`球队基础ID`) 
      ON DELETE CASCADE,
  CONSTRAINT `fk_ttp_tournament` 
      FOREIGN KEY (`赛事ID`) REFERENCES `tournament` (`赛事ID`) 
      ON DELETE CASCADE,
  -- 数据完整性检查
  CONSTRAINT `ttp_chk_1`  CHECK (`赛事总进球数`  >= 0),
  CONSTRAINT `ttp_chk_2`  CHECK (`赛事总失球数量` >= 0),
  CONSTRAINT `ttp_chk_3`  CHECK (`赛事红牌数`   >= 0),
  CONSTRAINT `ttp_chk_4`  CHECK (`赛事黄牌数`   >= 0),
  CONSTRAINT `ttp_chk_5`  CHECK (`赛事积分`     >= 0),
  CONSTRAINT `ttp_chk_6`  CHECK (`赛事排名` IS NULL OR `赛事排名` > 0),
  CONSTRAINT `ttp_chk_7`  CHECK (`比赛轮数`     >= 0),
  CONSTRAINT `ttp_chk_8`  CHECK (`胜场数`       >= 0),
  CONSTRAINT `ttp_chk_9`  CHECK (`平场数`       >= 0),
  CONSTRAINT `ttp_chk_10` CHECK (`负场数`       >= 0),
  CONSTRAINT `ttp_chk_11` CHECK (`比赛轮数` = `胜场数` + `平场数` + `负场数`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb3;

-- =============================
-- 保持向后兼容的视图 (team)
-- 为了不影响现有代码，创建一个视图模拟原来的team表
-- =============================
CREATE VIEW `team` AS
SELECT 
    ttp.`参与ID` AS `球队ID`,
    tb.`球队名称` AS `球队名称`,
    ttp.`小组ID` AS `小组ID`,
    ttp.`赛事ID` AS `赛事ID`,
    ttp.`赛事总进球数` AS `赛事总进球数`,
    ttp.`赛事总失球数量` AS `赛事总失球数量`,
    ttp.`赛事总净胜球` AS `赛事总净胜球`,
    ttp.`赛事红牌数` AS `赛事红牌数`,
    ttp.`赛事黄牌数` AS `赛事黄牌数`,
    ttp.`赛事积分` AS `赛事积分`,
    ttp.`赛事排名` AS `赛事排名`,
    ttp.`比赛轮数` AS `比赛轮数`,
    ttp.`胜场数` AS `胜场数`,
    ttp.`平场数` AS `平场数`,
    ttp.`负场数` AS `负场数`,
    -- 附加信息
    tb.`球队基础ID` AS `球队基础ID`,
    ttp.`状态` AS `参与状态`
FROM `team_tournament_participation` ttp
JOIN `team_base` tb ON ttp.`球队基础ID` = tb.`球队基础ID`
WHERE ttp.`状态` = 'active';


-- =============================
-- player 表
-- =============================
DROP TABLE IF EXISTS `player`;
CREATE TABLE `player` (
  `球员ID` varchar(20) NOT NULL,
  `球员姓名` varchar(50) NOT NULL,
  `职业生涯总进球数` int DEFAULT '0',
  `职业生涯总红牌数` int DEFAULT '0',
  `职业生涯总黄牌数` int DEFAULT '0',
  PRIMARY KEY (`球员ID`),
  CONSTRAINT `player_chk_1` CHECK ((`职业生涯总进球数` >= 0)),
  CONSTRAINT `player_chk_2` CHECK ((`职业生涯总红牌数` >= 0)),
  CONSTRAINT `player_chk_3` CHECK ((`职业生涯总黄牌数` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;


-- =============================
-- player_team_history 表
-- =============================
DROP TABLE IF EXISTS `player_team_history`;
CREATE TABLE `player_team_history` (
  `记录ID` int NOT NULL AUTO_INCREMENT,
  `球员ID` varchar(20) NOT NULL,
  `球员号码` int NOT NULL,
  `球队ID` int DEFAULT NULL COMMENT '引用team_tournament_participation表的参与ID',
  `赛事ID` int NOT NULL,
  `赛事进球数` int DEFAULT '0',
  `赛事红牌数` int DEFAULT '0',
  `赛事黄牌数` int DEFAULT '0',
  `备注` text,
  PRIMARY KEY (`记录ID`),
  UNIQUE KEY `unique_active_player_team_tournament` (`球员ID`,`球队ID`,`赛事ID`),
  KEY `fk_pth_tournament` (`赛事ID`),
  KEY `idx_team_tournament` (`球队ID`,`赛事ID`),
  KEY `idx_player_tournament` (`球员ID`,`赛事ID`),
  CONSTRAINT `fk_pth_player` FOREIGN KEY (`球员ID`) REFERENCES `player` (`球员ID`) ON DELETE CASCADE,
  CONSTRAINT `fk_pth_team_participation` FOREIGN KEY (`球队ID`) REFERENCES `team_tournament_participation` (`参与ID`) ON DELETE CASCADE,
  CONSTRAINT `fk_pth_tournament` FOREIGN KEY (`赛事ID`) REFERENCES `tournament` (`赛事ID`) ON DELETE CASCADE,
  CONSTRAINT `player_team_history_chk_1` CHECK ((`赛事进球数` >= 0)),
  CONSTRAINT `player_team_history_chk_2` CHECK ((`赛事红牌数` >= 0)),
  CONSTRAINT `player_team_history_chk_3` CHECK ((`赛事黄牌数` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- =============================
-- match 表
-- =============================
DROP TABLE IF EXISTS `match`;
CREATE TABLE `match` (
  `MatchID` varchar(50) NOT NULL,
  `比赛名称` varchar(50) NOT NULL,
  `赛事ID` int NOT NULL,
  `小组ID` char(1) DEFAULT NULL,
  `比赛时间` datetime NOT NULL,
  `比赛地点` varchar(50) NOT NULL,
  `主队ID` int DEFAULT NULL COMMENT '引用team_tournament_participation表的参与ID',
  `客队ID` int DEFAULT NULL COMMENT '引用team_tournament_participation表的参与ID',
  `主队比分` int DEFAULT '0',
  `客队比分` int DEFAULT '0',
  `比赛状态` char(1) NOT NULL,
  `淘汰赛轮次` int DEFAULT NULL,
  PRIMARY KEY (`MatchID`),
  KEY `idx_match_home_team` (`主队ID`),
  KEY `idx_match_away_team` (`客队ID`),
  KEY `idx_match_tournament` (`赛事ID`),
  KEY `idx_match_time` (`比赛时间`),
  KEY `idx_match_status` (`比赛状态`),
  CONSTRAINT `fk_match_away_team` FOREIGN KEY (`客队ID`) REFERENCES `team_tournament_participation` (`参与ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_match_home_team` FOREIGN KEY (`主队ID`) REFERENCES `team_tournament_participation` (`参与ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_match_tournament` FOREIGN KEY (`赛事ID`) REFERENCES `tournament` (`赛事ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `match_chk_1` CHECK ((`比赛状态` in ('F','P')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- =============================
-- event 表
-- =============================
DROP TABLE IF EXISTS `event`;
CREATE TABLE `event` (
  `eventID` int NOT NULL AUTO_INCREMENT,
  `MatchID` varchar(50) NOT NULL,
  `事件类型` varchar(50) NOT NULL,
  `球队ID` int NOT NULL COMMENT '引用team_tournament_participation表的参与ID，必填确保统计准确',
  `球员ID` varchar(20) NOT NULL,
  `事件时间` int DEFAULT NULL COMMENT '事件发生时间（比赛第几分钟）',
  PRIMARY KEY (`eventID`),
  KEY `idx_event_match` (`MatchID`),
  KEY `idx_event_team` (`球队ID`),
  KEY `idx_event_player` (`球员ID`),
  KEY `idx_event_type` (`事件类型`),
  CONSTRAINT `fk_event_match` FOREIGN KEY (`MatchID`) REFERENCES `match` (`MatchID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_event_player` FOREIGN KEY (`球员ID`) REFERENCES `player` (`球员ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_event_team` FOREIGN KEY (`球队ID`) REFERENCES `team_tournament_participation` (`参与ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- =============================
-- user 表
-- =============================
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `用户ID` int NOT NULL AUTO_INCREMENT,
  `用户名` varchar(50) NOT NULL,
  `密码` varchar(255) NOT NULL,
  `邮箱` varchar(100) NOT NULL,
  `身份角色` varchar(20) NOT NULL DEFAULT 'user',
  `创建时间` datetime DEFAULT CURRENT_TIMESTAMP,
  `最后登录时间` datetime DEFAULT NULL,
  `状态` char(1) DEFAULT 'A',
  PRIMARY KEY (`用户ID`),
  UNIQUE KEY `用户名` (`用户名`),
  UNIQUE KEY `邮箱` (`邮箱`),
  CONSTRAINT `user_chk_1` CHECK ((`状态` in ('A','D')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- =============================
-- team_tournament_participation 表的触发器
-- 由于 MySQL 不支持视图上的 INSTEAD OF 触发器，
-- 我们在实际表上创建触发器来维护数据一致性
-- =============================

DELIMITER $$

-- 在插入新的球队参与记录时，自动创建基础球队信息（如果不存在）
CREATE TRIGGER trg_ttp_before_insert
BEFORE INSERT ON team_tournament_participation
FOR EACH ROW
BEGIN
    DECLARE v_team_exists INT DEFAULT 0;
    
    -- 检查球队基础ID是否存在
    SELECT COUNT(*) INTO v_team_exists 
    FROM team_base 
    WHERE `球队基础ID` = NEW.`球队基础ID`;
    
    -- 如果球队基础信息不存在，抛出错误
    IF v_team_exists = 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '球队基础ID不存在，请先在team_base表中创建球队基础信息';
    END IF;
    
    -- 自动计算净胜球
    SET NEW.`赛事总净胜球` = NEW.`赛事总进球数` - NEW.`赛事总失球数量`;
END$$

-- 在更新球队参与记录时，自动重新计算净胜球
CREATE TRIGGER trg_ttp_before_update
BEFORE UPDATE ON team_tournament_participation
FOR EACH ROW
BEGIN
    -- 自动重新计算净胜球
    SET NEW.`赛事总净胜球` = NEW.`赛事总进球数` - NEW.`赛事总失球数量`;
END$$

DELIMITER ;


DELIMITER $$

CREATE TRIGGER after_event_insert
AFTER INSERT ON event
FOR EACH ROW
BEGIN
    DECLARE v_home   INT DEFAULT NULL;
    DECLARE v_away   INT DEFAULT NULL;
    DECLARE v_tour   INT DEFAULT NULL;
    DECLARE v_match_status CHAR(1) DEFAULT NULL;
    DECLARE v_team_exists INT DEFAULT 0;

    /* 1. 空值保护 - 确保球队ID不为空 */
    IF NEW.球队ID IS NULL THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '事件必须指定有效的球队ID';
    END IF;

    /* 2. 取比赛信息 */
    SELECT 主队ID, 客队ID, 赛事ID, 比赛状态
      INTO v_home, v_away, v_tour, v_match_status
    FROM `match`
    WHERE MatchID = NEW.MatchID;

    /* 3. 比赛信息验证 */
    IF v_home IS NULL OR v_away IS NULL OR v_tour IS NULL THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '比赛信息不存在或不完整';
    END IF;

    /* 4. 验证球队是否参与此比赛 */
    IF NEW.球队ID != v_home AND NEW.球队ID != v_away THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '球队未参与此比赛';
    END IF;

    /* 5. 验证球队在赛事中是否存在 */
    SELECT COUNT(*) INTO v_team_exists
    FROM team_tournament_participation
    WHERE 参与ID = NEW.球队ID AND 赛事ID = v_tour AND 状态 = 'active';
    
    IF v_team_exists = 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '球队未报名参与此赛事或状态异常';
    END IF;

    /* 6. 检查比赛状态 - 只允许进行中的比赛记录事件 */
    IF v_match_status = 'F' THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '比赛已结束，不允许添加新事件';
    END IF;

    /* 7. 根据事件类型更新统计 */
    CASE NEW.事件类型
        WHEN '进球' THEN
            /* 7.1 更新比分 */
            IF NEW.球队ID = v_home THEN
                UPDATE `match` SET 主队比分 = 主队比分 + 1 WHERE MatchID = NEW.MatchID;
                UPDATE team_tournament_participation 
                SET 赛事总失球数量 = 赛事总失球数量 + 1,
                    赛事总净胜球 = 赛事总进球数 - (赛事总失球数量 + 1)
                WHERE 参与ID = v_away AND 赛事ID = v_tour;
            ELSEIF NEW.球队ID = v_away THEN
                UPDATE `match` SET 客队比分 = 客队比分 + 1 WHERE MatchID = NEW.MatchID;
                UPDATE team_tournament_participation 
                SET 赛事总失球数量 = 赛事总失球数量 + 1,
                    赛事总净胜球 = 赛事总进球数 - (赛事总失球数量 + 1)
                WHERE 参与ID = v_home AND 赛事ID = v_tour;
            END IF;

            /* 7.2 更新进球方数据 */
            UPDATE team_tournament_participation
               SET 赛事总进球数 = 赛事总进球数 + 1,
                   赛事总净胜球 = (赛事总进球数 + 1) - 赛事总失球数量
             WHERE 参与ID = NEW.球队ID AND 赛事ID = v_tour;

            /* 7.3 更新球员统计 */
            UPDATE player
               SET 职业生涯总进球数 = 职业生涯总进球数 + 1
             WHERE 球员ID = NEW.球员ID;

            UPDATE player_team_history
               SET 赛事进球数 = 赛事进球数 + 1
             WHERE 球员ID = NEW.球员ID
               AND 球队ID = NEW.球队ID
               AND 赛事ID = v_tour;

        WHEN '乌龙球' THEN
            IF NEW.球队ID = v_home THEN
                UPDATE `match` SET 客队比分 = 客队比分 + 1 WHERE MatchID = NEW.MatchID;
                UPDATE team_tournament_participation 
                SET 赛事总失球数量 = 赛事总失球数量 + 1,
                    赛事总净胜球 = 赛事总进球数 - (赛事总失球数量 + 1)
                WHERE 参与ID = v_home AND 赛事ID = v_tour;
            ELSEIF NEW.球队ID = v_away THEN
                UPDATE `match` SET 主队比分 = 主队比分 + 1 WHERE MatchID = NEW.MatchID;
                UPDATE team_tournament_participation 
                SET 赛事总失球数量 = 赛事总失球数量 + 1,
                    赛事总净胜球 = 赛事总进球数 - (赛事总失球数量 + 1)
                WHERE 参与ID = v_away AND 赛事ID = v_tour;
            END IF;

        WHEN '红牌' THEN
            UPDATE team_tournament_participation
               SET 赛事红牌数 = 赛事红牌数 + 1
             WHERE 参与ID = NEW.球队ID AND 赛事ID = v_tour;

            UPDATE player
               SET 职业生涯总红牌数 = 职业生涯总红牌数 + 1
             WHERE 球员ID = NEW.球员ID;

            UPDATE player_team_history
               SET 赛事红牌数 = 赛事红牌数 + 1
             WHERE 球员ID = NEW.球员ID
               AND 球队ID = NEW.球队ID
               AND 赛事ID = v_tour;

        WHEN '黄牌' THEN
            UPDATE team_tournament_participation
               SET 赛事黄牌数 = 赛事黄牌数 + 1
             WHERE 参与ID = NEW.球队ID AND 赛事ID = v_tour;

            UPDATE player
               SET 职业生涯总黄牌数 = 职业生涯总黄牌数 + 1
             WHERE 球员ID = NEW.球员ID;

            UPDATE player_team_history
               SET 赛事黄牌数 = 赛事黄牌数 + 1
             WHERE 球员ID = NEW.球员ID
               AND 球队ID = NEW.球队ID
               AND 赛事ID = v_tour;
    END CASE;
END$$

DELIMITER ;
DELIMITER $$

CREATE TRIGGER after_event_update
AFTER UPDATE ON event
FOR EACH ROW
BEGIN
    DECLARE v_home INT DEFAULT NULL;
    DECLARE v_away INT DEFAULT NULL;
    DECLARE v_tour INT DEFAULT NULL;
    DECLARE v_match_status CHAR(1) DEFAULT NULL;
    DECLARE v_old_team_exists, v_new_team_exists INT DEFAULT 0;

    /* 1. 空值保护 */
    IF NEW.球队ID IS NULL THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '事件必须指定有效的球队ID';
    END IF;

    /* 2. 取比赛信息 */
    SELECT 主队ID, 客队ID, 赛事ID, 比赛状态
      INTO v_home, v_away, v_tour, v_match_status
    FROM `match`
    WHERE MatchID = NEW.MatchID;

    /* 3. 比赛信息验证 */
    IF v_home IS NULL OR v_away IS NULL OR v_tour IS NULL THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '比赛信息不存在或不完整';
    END IF;

    /* 4. 检查比赛状态 - 已结束的比赛不允许修改事件 */
    IF v_match_status = 'F' THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '比赛已结束，不允许修改事件';
    END IF;

    /* 5. 验证球队存在性 */
    SELECT COUNT(*) INTO v_old_team_exists
    FROM team_tournament_participation
    WHERE 参与ID = OLD.球队ID AND 赛事ID = v_tour AND 状态 = 'active';
    
    SELECT COUNT(*) INTO v_new_team_exists
    FROM team_tournament_participation
    WHERE 参与ID = NEW.球队ID AND 赛事ID = v_tour AND 状态 = 'active';
    
    IF v_old_team_exists = 0 OR v_new_team_exists = 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '相关球队记录不存在或状态异常';
    END IF;

    /* 6. 优化：如果球队和事件类型都没变，跳过处理 */
    IF OLD.球队ID = NEW.球队ID AND OLD.事件类型 = NEW.事件类型 THEN
        /* 无需任何统计更新 */
        SET @dummy = 1;
    ELSE
        /* 7. 回滚旧事件统计（OLD） */
        CASE OLD.事件类型
            WHEN '进球' THEN
                IF OLD.球队ID = v_home THEN
                    UPDATE `match` SET 主队比分 = GREATEST(主队比分 - 1, 0) WHERE MatchID = OLD.MatchID;
                    UPDATE team_tournament_participation 
                    SET 赛事总失球数量 = CASE WHEN 赛事总失球数量 > 0 THEN 赛事总失球数量 - 1 ELSE 0 END,
                        赛事总净胜球 = 赛事总进球数 - CASE WHEN 赛事总失球数量 > 0 THEN 赛事总失球数量 - 1 ELSE 0 END
                    WHERE 参与ID = v_away AND 赛事ID = v_tour;
                ELSEIF OLD.球队ID = v_away THEN
                    UPDATE `match` SET 客队比分 = GREATEST(客队比分 - 1, 0) WHERE MatchID = OLD.MatchID;
                    UPDATE team_tournament_participation 
                    SET 赛事总失球数量 = CASE WHEN 赛事总失球数量 > 0 THEN 赛事总失球数量 - 1 ELSE 0 END,
                        赛事总净胜球 = 赛事总进球数 - CASE WHEN 赛事总失球数量 > 0 THEN 赛事总失球数量 - 1 ELSE 0 END
                    WHERE 参与ID = v_home AND 赛事ID = v_tour;
                END IF;

                UPDATE team_tournament_participation
                   SET 赛事总进球数 = CASE WHEN 赛事总进球数 > 0 THEN 赛事总进球数 - 1 ELSE 0 END,
                       赛事总净胜球 = CASE WHEN 赛事总进球数 > 0 THEN 赛事总进球数 - 1 ELSE 0 END - 赛事总失球数量
                 WHERE 参与ID = OLD.球队ID AND 赛事ID = v_tour;

                UPDATE player
                   SET 职业生涯总进球数 = CASE WHEN 职业生涯总进球数 > 0 THEN 职业生涯总进球数 - 1 ELSE 0 END
                 WHERE 球员ID = OLD.球员ID;

                UPDATE player_team_history
                   SET 赛事进球数 = CASE WHEN 赛事进球数 > 0 THEN 赛事进球数 - 1 ELSE 0 END
                 WHERE 球员ID = OLD.球员ID AND 球队ID = OLD.球队ID AND 赛事ID = v_tour;

            WHEN '乌龙球' THEN
                IF OLD.球队ID = v_home THEN
                    UPDATE `match` SET 客队比分 = GREATEST(客队比分 - 1, 0) WHERE MatchID = OLD.MatchID;
                    UPDATE team_tournament_participation 
                    SET 赛事总失球数量 = CASE WHEN 赛事总失球数量 > 0 THEN 赛事总失球数量 - 1 ELSE 0 END,
                        赛事总净胜球 = 赛事总进球数 - CASE WHEN 赛事总失球数量 > 0 THEN 赛事总失球数量 - 1 ELSE 0 END
                    WHERE 参与ID = v_home AND 赛事ID = v_tour;
                ELSEIF OLD.球队ID = v_away THEN
                    UPDATE `match` SET 主队比分 = GREATEST(主队比分 - 1, 0) WHERE MatchID = OLD.MatchID;
                    UPDATE team_tournament_participation 
                    SET 赛事总失球数量 = CASE WHEN 赛事总失球数量 > 0 THEN 赛事总失球数量 - 1 ELSE 0 END,
                        赛事总净胜球 = 赛事总进球数 - CASE WHEN 赛事总失球数量 > 0 THEN 赛事总失球数量 - 1 ELSE 0 END
                    WHERE 参与ID = v_away AND 赛事ID = v_tour;
                END IF;

            WHEN '红牌' THEN
                UPDATE team_tournament_participation 
                SET 赛事红牌数 = CASE WHEN 赛事红牌数 > 0 THEN 赛事红牌数 - 1 ELSE 0 END
                WHERE 参与ID = OLD.球队ID AND 赛事ID = v_tour;
                
                UPDATE player 
                SET 职业生涯总红牌数 = CASE WHEN 职业生涯总红牌数 > 0 THEN 职业生涯总红牌数 - 1 ELSE 0 END
                WHERE 球员ID = OLD.球员ID;
                
                UPDATE player_team_history 
                SET 赛事红牌数 = CASE WHEN 赛事红牌数 > 0 THEN 赛事红牌数 - 1 ELSE 0 END
                WHERE 球员ID = OLD.球员ID AND 球队ID = OLD.球队ID AND 赛事ID = v_tour;

            WHEN '黄牌' THEN
                UPDATE team_tournament_participation 
                SET 赛事黄牌数 = CASE WHEN 赛事黄牌数 > 0 THEN 赛事黄牌数 - 1 ELSE 0 END
                WHERE 参与ID = OLD.球队ID AND 赛事ID = v_tour;
                
                UPDATE player 
                SET 职业生涯总黄牌数 = CASE WHEN 职业生涯总黄牌数 > 0 THEN 职业生涯总黄牌数 - 1 ELSE 0 END
                WHERE 球员ID = OLD.球员ID;
                
                UPDATE player_team_history 
                SET 赛事黄牌数 = CASE WHEN 赛事黄牌数 > 0 THEN 赛事黄牌数 - 1 ELSE 0 END
                WHERE 球员ID = OLD.球员ID AND 球队ID = OLD.球队ID AND 赛事ID = v_tour;
        END CASE;

        /* 8. 应用新事件统计（NEW） */
        CASE NEW.事件类型
            WHEN '进球' THEN
                IF NEW.球队ID = v_home THEN
                    UPDATE `match` SET 主队比分 = 主队比分 + 1 WHERE MatchID = NEW.MatchID;
                    UPDATE team_tournament_participation 
                    SET 赛事总失球数量 = 赛事总失球数量 + 1,
                        赛事总净胜球 = 赛事总进球数 - (赛事总失球数量 + 1)
                    WHERE 参与ID = v_away AND 赛事ID = v_tour;
                ELSEIF NEW.球队ID = v_away THEN
                    UPDATE `match` SET 客队比分 = 客队比分 + 1 WHERE MatchID = NEW.MatchID;
                    UPDATE team_tournament_participation 
                    SET 赛事总失球数量 = 赛事总失球数量 + 1,
                        赛事总净胜球 = 赛事总进球数 - (赛事总失球数量 + 1)
                    WHERE 参与ID = v_home AND 赛事ID = v_tour;
                END IF;

                UPDATE team_tournament_participation
                   SET 赛事总进球数 = 赛事总进球数 + 1,
                       赛事总净胜球 = (赛事总进球数 + 1) - 赛事总失球数量
                 WHERE 参与ID = NEW.球队ID AND 赛事ID = v_tour;

                UPDATE player
                   SET 职业生涯总进球数 = 职业生涯总进球数 + 1
                 WHERE 球员ID = NEW.球员ID;

                UPDATE player_team_history
                   SET 赛事进球数 = 赛事进球数 + 1
                 WHERE 球员ID = NEW.球员ID AND 球队ID = NEW.球队ID AND 赛事ID = v_tour;

            WHEN '乌龙球' THEN
                IF NEW.球队ID = v_home THEN
                    UPDATE `match` SET 客队比分 = 客队比分 + 1 WHERE MatchID = NEW.MatchID;
                    UPDATE team_tournament_participation 
                    SET 赛事总失球数量 = 赛事总失球数量 + 1,
                        赛事总净胜球 = 赛事总进球数 - (赛事总失球数量 + 1)
                    WHERE 参与ID = v_home AND 赛事ID = v_tour;
                ELSEIF NEW.球队ID = v_away THEN
                    UPDATE `match` SET 主队比分 = 主队比分 + 1 WHERE MatchID = NEW.MatchID;
                    UPDATE team_tournament_participation 
                    SET 赛事总失球数量 = 赛事总失球数量 + 1,
                        赛事总净胜球 = 赛事总进球数 - (赛事总失球数量 + 1)
                    WHERE 参与ID = v_away AND 赛事ID = v_tour;
                END IF;

            WHEN '红牌' THEN
                UPDATE team_tournament_participation 
                SET 赛事红牌数 = 赛事红牌数 + 1
                WHERE 参与ID = NEW.球队ID AND 赛事ID = v_tour;
                
                UPDATE player 
                SET 职业生涯总红牌数 = 职业生涯总红牌数 + 1
                WHERE 球员ID = NEW.球员ID;
                
                UPDATE player_team_history 
                SET 赛事红牌数 = 赛事红牌数 + 1
                WHERE 球员ID = NEW.球员ID AND 球队ID = NEW.球队ID AND 赛事ID = v_tour;

            WHEN '黄牌' THEN
                UPDATE team_tournament_participation 
                SET 赛事黄牌数 = 赛事黄牌数 + 1
                WHERE 参与ID = NEW.球队ID AND 赛事ID = v_tour;
                
                UPDATE player 
                SET 职业生涯总黄牌数 = 职业生涯总黄牌数 + 1
                WHERE 球员ID = NEW.球员ID;
                
                UPDATE player_team_history 
                SET 赛事黄牌数 = 赛事黄牌数 + 1
                WHERE 球员ID = NEW.球员ID AND 球队ID = NEW.球队ID AND 赛事ID = v_tour;
        END CASE;
    END IF;
END$$

DELIMITER ;
DELIMITER $$

CREATE TRIGGER after_event_delete
AFTER DELETE ON event
FOR EACH ROW
BEGIN
    DECLARE v_home INT DEFAULT NULL;
    DECLARE v_away INT DEFAULT NULL;
    DECLARE v_tour INT DEFAULT NULL;
    DECLARE v_match_status CHAR(1) DEFAULT NULL;
    DECLARE v_team_exists INT DEFAULT 0;
    DECLARE v_affected_rows INT DEFAULT 0;

    /* 1. 空值保护 */
    IF OLD.球队ID IS NULL THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '无法处理球队ID为空的事件删除';
    END IF;

    /* 2. 取比赛信息 */
    SELECT 主队ID, 客队ID, 赛事ID, 比赛状态
      INTO v_home, v_away, v_tour, v_match_status
    FROM `match`
    WHERE MatchID = OLD.MatchID;

    /* 3. 比赛信息验证 */
    IF v_home IS NULL OR v_away IS NULL OR v_tour IS NULL THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '比赛信息不存在，无法回滚统计';
    END IF;

    /* 4. 检查比赛状态 - 已结束的比赛不允许删除事件 */
    IF v_match_status = 'F' THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '比赛已结束，不允许删除事件';
    END IF;

    /* 5. 验证球队记录存在性 */
    SELECT COUNT(*) INTO v_team_exists
    FROM team_tournament_participation
    WHERE 参与ID = OLD.球队ID AND 赛事ID = v_tour AND 状态 = 'active';
    
    IF v_team_exists = 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '球队记录不存在或状态异常，无法回滚统计';
    END IF;

    /* 6. 根据被删除的事件类型回滚统计 */
    CASE OLD.事件类型
        WHEN '进球' THEN
            /* 6.1 比分与失球回滚 */
            IF OLD.球队ID = v_home THEN
                UPDATE `match`
                   SET 主队比分 = CASE WHEN 主队比分 > 0 THEN 主队比分 - 1 ELSE 0 END
                 WHERE MatchID = OLD.MatchID;
                 
                UPDATE team_tournament_participation
                   SET 赛事总失球数量 = CASE WHEN 赛事总失球数量 > 0 THEN 赛事总失球数量 - 1 ELSE 0 END,
                       赛事总净胜球 = 赛事总进球数 - CASE WHEN 赛事总失球数量 > 0 THEN 赛事总失球数量 - 1 ELSE 0 END
                 WHERE 参与ID = v_away AND 赛事ID = v_tour;
                 
            ELSEIF OLD.球队ID = v_away THEN
                UPDATE `match`
                   SET 客队比分 = CASE WHEN 客队比分 > 0 THEN 客队比分 - 1 ELSE 0 END
                 WHERE MatchID = OLD.MatchID;
                 
                UPDATE team_tournament_participation
                   SET 赛事总失球数量 = CASE WHEN 赛事总失球数量 > 0 THEN 赛事总失球数量 - 1 ELSE 0 END,
                       赛事总净胜球 = 赛事总进球数 - CASE WHEN 赛事总失球数量 > 0 THEN 赛事总失球数量 - 1 ELSE 0 END
                 WHERE 参与ID = v_home AND 赛事ID = v_tour;
            END IF;

            /* 6.2 球队进球、净胜球回滚 */
            UPDATE team_tournament_participation
               SET 赛事总进球数 = CASE WHEN 赛事总进球数 > 0 THEN 赛事总进球数 - 1 ELSE 0 END,
                   赛事总净胜球 = CASE WHEN 赛事总进球数 > 0 THEN 赛事总进球数 - 1 ELSE 0 END - 赛事总失球数量
             WHERE 参与ID = OLD.球队ID AND 赛事ID = v_tour;
             
            GET DIAGNOSTICS v_affected_rows = ROW_COUNT;
            IF v_affected_rows = 0 THEN
                SIGNAL SQLSTATE '45000' 
                SET MESSAGE_TEXT = '球队统计更新失败，数据可能已被删除';
            END IF;

            /* 6.3 球员进球回滚 */
            UPDATE player
               SET 职业生涯总进球数 = CASE WHEN 职业生涯总进球数 > 0 THEN 职业生涯总进球数 - 1 ELSE 0 END
             WHERE 球员ID = OLD.球员ID;

            UPDATE player_team_history
               SET 赛事进球数 = CASE WHEN 赛事进球数 > 0 THEN 赛事进球数 - 1 ELSE 0 END
             WHERE 球员ID = OLD.球员ID
               AND 球队ID = OLD.球队ID
               AND 赛事ID = v_tour;

        WHEN '乌龙球' THEN
            IF OLD.球队ID = v_home THEN
                UPDATE `match`
                   SET 客队比分 = CASE WHEN 客队比分 > 0 THEN 客队比分 - 1 ELSE 0 END
                 WHERE MatchID = OLD.MatchID;
                UPDATE team_tournament_participation
                   SET 赛事总失球数量 = CASE WHEN 赛事总失球数量 > 0 THEN 赛事总失球数量 - 1 ELSE 0 END,
                       赛事总净胜球 = 赛事总进球数 - CASE WHEN 赛事总失球数量 > 0 THEN 赛事总失球数量 - 1 ELSE 0 END
                 WHERE 参与ID = v_home AND 赛事ID = v_tour;
            ELSEIF OLD.球队ID = v_away THEN
                UPDATE `match`
                   SET 主队比分 = CASE WHEN 主队比分 > 0 THEN 主队比分 - 1 ELSE 0 END
                 WHERE MatchID = OLD.MatchID;
                UPDATE team_tournament_participation
                   SET 赛事总失球数量 = CASE WHEN 赛事总失球数量 > 0 THEN 赛事总失球数量 - 1 ELSE 0 END,
                       赛事总净胜球 = 赛事总进球数 - CASE WHEN 赛事总失球数量 > 0 THEN 赛事总失球数量 - 1 ELSE 0 END
                 WHERE 参与ID = v_away AND 赛事ID = v_tour;
            END IF;

        WHEN '红牌' THEN
            UPDATE team_tournament_participation
               SET 赛事红牌数 = CASE WHEN 赛事红牌数 > 0 THEN 赛事红牌数 - 1 ELSE 0 END
             WHERE 参与ID = OLD.球队ID AND 赛事ID = v_tour;
             
            GET DIAGNOSTICS v_affected_rows = ROW_COUNT;
            IF v_affected_rows = 0 THEN
                SIGNAL SQLSTATE '45000' 
                SET MESSAGE_TEXT = '球队红牌统计更新失败';
            END IF;
            
            UPDATE player
               SET 职业生涯总红牌数 = CASE WHEN 职业生涯总红牌数 > 0 THEN 职业生涯总红牌数 - 1 ELSE 0 END
             WHERE 球员ID = OLD.球员ID;
             
            UPDATE player_team_history
               SET 赛事红牌数 = CASE WHEN 赛事红牌数 > 0 THEN 赛事红牌数 - 1 ELSE 0 END
             WHERE 球员ID = OLD.球员ID
               AND 球队ID = OLD.球队ID
               AND 赛事ID = v_tour;

        WHEN '黄牌' THEN
            UPDATE team_tournament_participation
               SET 赛事黄牌数 = CASE WHEN 赛事黄牌数 > 0 THEN 赛事黄牌数 - 1 ELSE 0 END
             WHERE 参与ID = OLD.球队ID AND 赛事ID = v_tour;
             
            GET DIAGNOSTICS v_affected_rows = ROW_COUNT;
            IF v_affected_rows = 0 THEN
                SIGNAL SQLSTATE '45000' 
                SET MESSAGE_TEXT = '球队黄牌统计更新失败';
            END IF;
            
            UPDATE player
               SET 职业生涯总黄牌数 = CASE WHEN 职业生涯总黄牌数 > 0 THEN 职业生涯总黄牌数 - 1 ELSE 0 END
             WHERE 球员ID = OLD.球员ID;
             
            UPDATE player_team_history
               SET 赛事黄牌数 = CASE WHEN 赛事黄牌数 > 0 THEN 赛事黄牌数 - 1 ELSE 0 END
             WHERE 球员ID = OLD.球员ID
               AND 球队ID = OLD.球队ID
               AND 赛事ID = v_tour;
    END CASE;
END$$

DELIMITER ;

DELIMITER $$

CREATE TRIGGER trg_update_points_and_ranking_after_match_finish
AFTER UPDATE ON `match`
FOR EACH ROW
BEGIN
    DECLARE v_home_pts INT DEFAULT 0;
    DECLARE v_away_pts INT DEFAULT 0;
    DECLARE v_home_processed INT DEFAULT 0;
    DECLARE v_away_processed INT DEFAULT 0;
    DECLARE v_affected_rows INT DEFAULT 0;

    /* 缺陷修复A：防止重复计分 - 仅当比赛首次完成时才计分 */
    IF OLD.比赛状态 <> 'F' AND NEW.比赛状态 = 'F' THEN
        
        /* 1. 验证球队参与记录存在 */
        IF NEW.主队ID IS NULL OR NEW.客队ID IS NULL THEN
            SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = '比赛主客队信息不完整，无法计算积分';
        END IF;

        /* 2. 检查该比赛是否已经被处理过（防止重复计分） */
        SELECT COUNT(*) INTO v_home_processed
        FROM team_tournament_participation 
        WHERE 参与ID = NEW.主队ID 
          AND 赛事ID = NEW.赛事ID
          AND 比赛轮数 > 0;  -- 如果已有比赛记录，说明可能已处理

        SELECT COUNT(*) INTO v_away_processed  
        FROM team_tournament_participation 
        WHERE 参与ID = NEW.客队ID 
          AND 赛事ID = NEW.赛事ID
          AND 比赛轮数 > 0;

        /* 3. 计算本场比赛积分 */
        IF NEW.主队比分 > NEW.客队比分 THEN
            SET v_home_pts = 3;
            SET v_away_pts = 0;
        ELSEIF NEW.主队比分 < NEW.客队比分 THEN
            SET v_home_pts = 0;
            SET v_away_pts = 3;
        ELSE
            SET v_home_pts = 1;
            SET v_away_pts = 1;
        END IF;

        /* 4. 更新球队积分和比赛统计 */
        IF NEW.主队比分 > NEW.客队比分 THEN
            /* 主队胜 */
            UPDATE team_tournament_participation
               SET 赛事积分 = 赛事积分 + v_home_pts,
                   比赛轮数 = 比赛轮数 + 1,
                   胜场数 = 胜场数 + 1
             WHERE 参与ID = NEW.主队ID AND 赛事ID = NEW.赛事ID;
            
            GET DIAGNOSTICS v_affected_rows = ROW_COUNT;
            IF v_affected_rows = 0 THEN
                SIGNAL SQLSTATE '45000' 
                SET MESSAGE_TEXT = '主队积分更新失败，球队参与记录不存在';
            END IF;
            
            UPDATE team_tournament_participation
               SET 赛事积分 = 赛事积分 + v_away_pts,
                   比赛轮数 = 比赛轮数 + 1,
                   负场数 = 负场数 + 1
             WHERE 参与ID = NEW.客队ID AND 赛事ID = NEW.赛事ID;
             
            GET DIAGNOSTICS v_affected_rows = ROW_COUNT;
            IF v_affected_rows = 0 THEN
                SIGNAL SQLSTATE '45000' 
                SET MESSAGE_TEXT = '客队积分更新失败，球队参与记录不存在';
            END IF;
            
        ELSEIF NEW.主队比分 < NEW.客队比分 THEN
            /* 客队胜 */
            UPDATE team_tournament_participation
               SET 赛事积分 = 赛事积分 + v_home_pts,
                   比赛轮数 = 比赛轮数 + 1,
                   负场数 = 负场数 + 1
             WHERE 参与ID = NEW.主队ID AND 赛事ID = NEW.赛事ID;
             
            GET DIAGNOSTICS v_affected_rows = ROW_COUNT;
            IF v_affected_rows = 0 THEN
                SIGNAL SQLSTATE '45000' 
                SET MESSAGE_TEXT = '主队积分更新失败，球队参与记录不存在';
            END IF;
            
            UPDATE team_tournament_participation
               SET 赛事积分 = 赛事积分 + v_away_pts,
                   比赛轮数 = 比赛轮数 + 1,
                   胜场数 = 胜场数 + 1
             WHERE 参与ID = NEW.客队ID AND 赛事ID = NEW.赛事ID;
             
            GET DIAGNOSTICS v_affected_rows = ROW_COUNT;
            IF v_affected_rows = 0 THEN
                SIGNAL SQLSTATE '45000' 
                SET MESSAGE_TEXT = '客队积分更新失败，球队参与记录不存在';
            END IF;
        ELSE
            /* 平局 */
            UPDATE team_tournament_participation
               SET 赛事积分 = 赛事积分 + v_home_pts,
                   比赛轮数 = 比赛轮数 + 1,
                   平场数 = 平场数 + 1
             WHERE 参与ID = NEW.主队ID AND 赛事ID = NEW.赛事ID;
             
            GET DIAGNOSTICS v_affected_rows = ROW_COUNT;
            IF v_affected_rows = 0 THEN
                SIGNAL SQLSTATE '45000' 
                SET MESSAGE_TEXT = '主队积分更新失败，球队参与记录不存在';
            END IF;
            
            UPDATE team_tournament_participation
               SET 赛事积分 = 赛事积分 + v_away_pts,
                   比赛轮数 = 比赛轮数 + 1,
                   平场数 = 平场数 + 1
             WHERE 参与ID = NEW.客队ID AND 赛事ID = NEW.赛事ID;
             
            GET DIAGNOSTICS v_affected_rows = ROW_COUNT;
            IF v_affected_rows = 0 THEN
                SIGNAL SQLSTATE '45000' 
                SET MESSAGE_TEXT = '客队积分更新失败，球队参与记录不存在';
            END IF;
        END IF;

        /* 缺陷修复B：使用ROW_NUMBER()替代会话变量，避免竞态条件 */
        /* 5. 重新计算并写入排名 - 使用窗口函数确保线程安全 */
        UPDATE team_tournament_participation AS ttp
        JOIN (
            SELECT 参与ID,
                   ROW_NUMBER() OVER (
                       ORDER BY 赛事积分 DESC,
                                赛事总净胜球 DESC,
                                赛事总进球数 DESC,
                                参与ID ASC
                   ) AS new_rank
            FROM team_tournament_participation
            WHERE 赛事ID = NEW.赛事ID
              AND 状态 = 'active'
        ) AS ranking ON ttp.参与ID = ranking.参与ID
        SET ttp.赛事排名 = ranking.new_rank
        WHERE ttp.赛事ID = NEW.赛事ID AND ttp.状态 = 'active';
        
        GET DIAGNOSTICS v_affected_rows = ROW_COUNT;
        IF v_affected_rows = 0 THEN
            SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = '排名更新失败，请检查赛事参与记录';
        END IF;
    END IF;
    
    /* 6. 额外保护：如果比赛从已完成变回进行中，给出警告但不回滚数据 */
    /* 注意：此处不自动回滚，因为可能涉及复杂的业务逻辑，应由应用层处理 */
    IF OLD.比赛状态 = 'F' AND NEW.比赛状态 = 'P' THEN
        /* 这里只记录警告，不做数据回滚，避免触发器中处理过于复杂的逻辑 */
        /* 实际项目中应该在应用层禁止这种操作，或提供专门的回滚功能 */
        SIGNAL SQLSTATE '01000' 
        SET MESSAGE_TEXT = '警告：比赛状态从已完成改为进行中，积分和排名可能需要手动调整';
    END IF;
END$$

DELIMITER ;

-- =============================
-- 数据库架构清理完成
-- =============================
-- 保留了核心建表语句、触发器和兼容性视图
-- 删除了存储过程和示例查询，业务逻辑已迁移到后端服务
-- =============================
