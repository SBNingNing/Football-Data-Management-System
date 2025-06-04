USE football_management_system;

-- 先删除已存在的触发器
DROP TRIGGER IF EXISTS after_event_insert;
DROP TRIGGER IF EXISTS after_event_delete;
DROP TRIGGER IF EXISTS after_event_update;

-- 创建触发器：添加事件时自动更新统计数据
DELIMITER $$

CREATE TRIGGER after_event_insert
AFTER INSERT ON event
FOR EACH ROW
BEGIN
    DECLARE match_home_team INT DEFAULT NULL;
    DECLARE match_away_team INT DEFAULT NULL;
    DECLARE match_tournament INT DEFAULT NULL;
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
    
    -- 获取比赛信息，使用正确的字段名
    SELECT 主队ID, 客队ID, 赛事ID 
    INTO match_home_team, match_away_team, match_tournament
    FROM `match` 
    WHERE MatchID = NEW.MatchID;
    
    -- 检查是否成功获取比赛信息
    IF match_home_team IS NOT NULL AND match_away_team IS NOT NULL AND match_tournament IS NOT NULL THEN
        -- 根据事件类型更新相应统计
        CASE NEW.事件类型
            WHEN '进球' THEN
                -- 更新比赛比分
                IF NEW.球队ID = match_home_team THEN
                    UPDATE `match` SET 主队比分 = 主队比分 + 1 WHERE MatchID = NEW.MatchID;
                ELSEIF NEW.球队ID = match_away_team THEN
                    UPDATE `match` SET 客队比分 = 客队比分 + 1 WHERE MatchID = NEW.MatchID;
                END IF;
                
                -- 更新球队进球数
                UPDATE team SET 赛事总进球数 = 赛事总进球数 + 1 
                WHERE 球队ID = NEW.球队ID;
                
                -- 更新球员职业生涯进球数
                UPDATE player SET 职业生涯总进球数 = 职业生涯总进球数 + 1 
                WHERE 球员ID = NEW.球员ID;
                
                -- 更新球员在该赛事的进球数
                UPDATE player_team_history 
                SET 赛事进球数 = 赛事进球数 + 1 
                WHERE 球员ID = NEW.球员ID AND 球队ID = NEW.球队ID AND 赛事ID = match_tournament;
                
            WHEN '乌龙球' THEN
                -- 更新比赛比分（乌龙球给对方加分）
                IF NEW.球队ID = match_home_team THEN
                    UPDATE `match` SET 客队比分 = 客队比分 + 1 WHERE MatchID = NEW.MatchID;
                ELSEIF NEW.球队ID = match_away_team THEN
                    UPDATE `match` SET 主队比分 = 主队比分 + 1 WHERE MatchID = NEW.MatchID;
                END IF;
                
            WHEN '红牌' THEN
                -- 更新球队红牌数
                UPDATE team SET 赛事红牌数 = 赛事红牌数 + 1 
                WHERE 球队ID = NEW.球队ID;
                
                -- 更新球员职业生涯红牌数
                UPDATE player SET 职业生涯总红牌数 = 职业生涯总红牌数 + 1 
                WHERE 球员ID = NEW.球员ID;
                
                -- 更新球员在该赛事的红牌数
                UPDATE player_team_history 
                SET 赛事红牌数 = 赛事红牌数 + 1 
                WHERE 球员ID = NEW.球员ID AND 球队ID = NEW.球队ID AND 赛事ID = match_tournament;
                
            WHEN '黄牌' THEN
                -- 更新球队黄牌数
                UPDATE team SET 赛事黄牌数 = 赛事黄牌数 + 1 
                WHERE 球队ID = NEW.球队ID;
                
                -- 更新球员职业生涯黄牌数
                UPDATE player SET 职业生涯总黄牌数 = 职业生涯总黄牌数 + 1 
                WHERE 球员ID = NEW.球员ID;
                
                -- 更新球员在该赛事的黄牌数
                UPDATE player_team_history 
                SET 赛事黄牌数 = 赛事黄牌数 + 1 
                WHERE 球员ID = NEW.球员ID AND 球队ID = NEW.球队ID AND 赛事ID = match_tournament;
        END CASE;
    END IF;
END$$

-- 创建触发器：删除事件时自动回滚统计数据
CREATE TRIGGER after_event_delete
AFTER DELETE ON event
FOR EACH ROW
BEGIN
    DECLARE match_home_team INT DEFAULT NULL;
    DECLARE match_away_team INT DEFAULT NULL;
    DECLARE match_tournament INT DEFAULT NULL;
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
    
    -- 获取比赛信息
    SELECT 主队ID, 客队ID, 赛事ID 
    INTO match_home_team, match_away_team, match_tournament
    FROM `match` 
    WHERE MatchID = OLD.MatchID;
    
    -- 检查是否成功获取比赛信息
    IF match_home_team IS NOT NULL AND match_away_team IS NOT NULL AND match_tournament IS NOT NULL THEN
        -- 根据事件类型回滚相应统计
        CASE OLD.事件类型
            WHEN '进球' THEN
                -- 回滚比赛比分
                IF OLD.球队ID = match_home_team THEN
                    UPDATE `match` SET 主队比分 = GREATEST(主队比分 - 1, 0) WHERE MatchID = OLD.MatchID;
                ELSEIF OLD.球队ID = match_away_team THEN
                    UPDATE `match` SET 客队比分 = GREATEST(客队比分 - 1, 0) WHERE MatchID = OLD.MatchID;
                END IF;
                
                -- 回滚球队进球数
                UPDATE team SET 赛事总进球数 = GREATEST(赛事总进球数 - 1, 0) WHERE 球队ID = OLD.球队ID;
                UPDATE player SET 职业生涯总进球数 = GREATEST(职业生涯总进球数 - 1, 0) WHERE 球员ID = OLD.球员ID;
                UPDATE player_team_history SET 赛事进球数 = GREATEST(赛事进球数 - 1, 0) 
                WHERE 球员ID = OLD.球员ID AND 球队ID = OLD.球队ID AND 赛事ID = match_tournament;
                
            WHEN '乌龙球' THEN
                -- 回滚比赛比分（乌龙球是给对方球队加分）
                IF OLD.球队ID = match_home_team THEN
                    UPDATE `match` SET 客队比分 = GREATEST(客队比分 - 1, 0) WHERE MatchID = OLD.MatchID;
                ELSEIF OLD.球队ID = match_away_team THEN
                    UPDATE `match` SET 主队比分 = GREATEST(主队比分 - 1, 0) WHERE MatchID = OLD.MatchID;
                END IF;
                
            WHEN '红牌' THEN
                UPDATE team SET 赛事红牌数 = GREATEST(赛事红牌数 - 1, 0) WHERE 球队ID = OLD.球队ID;
                UPDATE player SET 职业生涯总红牌数 = GREATEST(职业生涯总红牌数 - 1, 0) WHERE 球员ID = OLD.球员ID;
                UPDATE player_team_history SET 赛事红牌数 = GREATEST(赛事红牌数 - 1, 0) 
                WHERE 球员ID = OLD.球员ID AND 球队ID = OLD.球队ID AND 赛事ID = match_tournament;
                
            WHEN '黄牌' THEN
                UPDATE team SET 赛事黄牌数 = GREATEST(赛事黄牌数 - 1, 0) WHERE 球队ID = OLD.球队ID;
                UPDATE player SET 职业生涯总黄牌数 = GREATEST(职业生涯总黄牌数 - 1, 0) WHERE 球员ID = OLD.球员ID;
                UPDATE player_team_history SET 赛事黄牌数 = GREATEST(赛事黄牌数 - 1, 0) 
                WHERE 球员ID = OLD.球员ID AND 球队ID = OLD.球队ID AND 赛事ID = match_tournament;
        END CASE;
    END IF;
END$$

-- 创建触发器：修改事件时自动更新统计数据
CREATE TRIGGER after_event_update
AFTER UPDATE ON event
FOR EACH ROW
BEGIN
    DECLARE match_home_team INT DEFAULT NULL;
    DECLARE match_away_team INT DEFAULT NULL;
    DECLARE match_tournament INT DEFAULT NULL;
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
    
    -- 获取比赛信息
    SELECT 主队ID, 客队ID, 赛事ID 
    INTO match_home_team, match_away_team, match_tournament
    FROM `match` 
    WHERE MatchID = NEW.MatchID;
    
    -- 检查是否成功获取比赛信息
    IF match_home_team IS NOT NULL AND match_away_team IS NOT NULL AND match_tournament IS NOT NULL THEN
        -- 先回滚旧事件的统计数据
        CASE OLD.事件类型
            WHEN '进球' THEN
                -- 回滚比赛比分
                IF OLD.球队ID = match_home_team THEN
                    UPDATE `match` SET 主队比分 = GREATEST(主队比分 - 1, 0) WHERE MatchID = OLD.MatchID;
                ELSEIF OLD.球队ID = match_away_team THEN
                    UPDATE `match` SET 客队比分 = GREATEST(客队比分 - 1, 0) WHERE MatchID = OLD.MatchID;
                END IF;
                
                -- 回滚球队进球数
                UPDATE team SET 赛事总进球数 = GREATEST(赛事总进球数 - 1, 0) WHERE 球队ID = OLD.球队ID;
                UPDATE player SET 职业生涯总进球数 = GREATEST(职业生涯总进球数 - 1, 0) WHERE 球员ID = OLD.球员ID;
                UPDATE player_team_history SET 赛事进球数 = GREATEST(赛事进球数 - 1, 0) 
                WHERE 球员ID = OLD.球员ID AND 球队ID = OLD.球队ID AND 赛事ID = match_tournament;
                
            WHEN '乌龙球' THEN
                -- 回滚比赛比分
                IF OLD.球队ID = match_home_team THEN
                    UPDATE `match` SET 客队比分 = GREATEST(客队比分 - 1, 0) WHERE MatchID = OLD.MatchID;
                ELSEIF OLD.球队ID = match_away_team THEN
                    UPDATE `match` SET 主队比分 = GREATEST(主队比分 - 1, 0) WHERE MatchID = OLD.MatchID;
                END IF;
                
            WHEN '红牌' THEN
                UPDATE team SET 赛事红牌数 = GREATEST(赛事红牌数 - 1, 0) WHERE 球队ID = OLD.球队ID;
                UPDATE player SET 职业生涯总红牌数 = GREATEST(职业生涯总红牌数 - 1, 0) WHERE 球员ID = OLD.球员ID;
                UPDATE player_team_history SET 赛事红牌数 = GREATEST(赛事红牌数 - 1, 0) 
                WHERE 球员ID = OLD.球员ID AND 球队ID = OLD.球队ID AND 赛事ID = match_tournament;
                
            WHEN '黄牌' THEN
                UPDATE team SET 赛事黄牌数 = GREATEST(赛事黄牌数 - 1, 0) WHERE 球队ID = OLD.球队ID;
                UPDATE player SET 职业生涯总黄牌数 = GREATEST(职业生涯总黄牌数 - 1, 0) WHERE 球员ID = OLD.球员ID;
                UPDATE player_team_history SET 赛事黄牌数 = GREATEST(赛事黄牌数 - 1, 0) 
                WHERE 球员ID = OLD.球员ID AND 球队ID = OLD.球队ID AND 赛事ID = match_tournament;
        END CASE;
        
        -- 再应用新事件的统计数据
        CASE NEW.事件类型
            WHEN '进球' THEN
                -- 更新比赛比分
                IF NEW.球队ID = match_home_team THEN
                    UPDATE `match` SET 主队比分 = 主队比分 + 1 WHERE MatchID = NEW.MatchID;
                ELSEIF NEW.球队ID = match_away_team THEN
                    UPDATE `match` SET 客队比分 = 客队比分 + 1 WHERE MatchID = NEW.MatchID;
                END IF;
                
                -- 更新球队进球数
                UPDATE team SET 赛事总进球数 = 赛事总进球数 + 1 
                WHERE 球队ID = NEW.球队ID;
                
                -- 更新球员职业生涯进球数
                UPDATE player SET 职业生涯总进球数 = 职业生涯总进球数 + 1 
                WHERE 球员ID = NEW.球员ID;
                
                -- 更新球员在该赛事的进球数
                UPDATE player_team_history 
                SET 赛事进球数 = 赛事进球数 + 1 
                WHERE 球员ID = NEW.球员ID AND 球队ID = NEW.球队ID AND 赛事ID = match_tournament;
                
            WHEN '乌龙球' THEN
                -- 更新比赛比分
                IF NEW.球队ID = match_home_team THEN
                    UPDATE `match` SET 客队比分 = 客队比分 + 1 WHERE MatchID = NEW.MatchID;
                ELSEIF NEW.球队ID = match_away_team THEN
                    UPDATE `match` SET 主队比分 = 主队比分 + 1 WHERE MatchID = NEW.MatchID;
                END IF;
                
            WHEN '红牌' THEN
                UPDATE team SET 赛事红牌数 = 赛事红牌数 + 1 WHERE 球队ID = NEW.球队ID;
                UPDATE player SET 职业生涯总红牌数 = 职业生涯总红牌数 + 1 WHERE 球员ID = NEW.球员ID;
                UPDATE player_team_history SET 赛事红牌数 = 赛事红牌数 + 1 
                WHERE 球员ID = NEW.球员ID AND 球队ID = NEW.球队ID AND 赛事ID = match_tournament;
                
            WHEN '黄牌' THEN
                UPDATE team SET 赛事黄牌数 = 赛事黄牌数 + 1 WHERE 球队ID = NEW.球队ID;
                UPDATE player SET 职业生涯总黄牌数 = 职业生涯总黄牌数 + 1 WHERE 球员ID = NEW.球员ID;
                UPDATE player_team_history SET 赛事黄牌数 = 赛事黄牌数 + 1 
                WHERE 球员ID = NEW.球员ID AND 球队ID = NEW.球队ID AND 赛事ID = match_tournament;
        END CASE;
    END IF;
END$$

DELIMITER ;

