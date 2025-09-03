CREATE DATABASE  IF NOT EXISTS `football_management_system` /*!40100 DEFAULT CHARACTER SET utf8mb3 */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `football_management_system`;
-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: football_management_system
-- ------------------------------------------------------
-- Server version	8.0.41

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `event`
--

DROP TABLE IF EXISTS `event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `event` (
  `eventID` int NOT NULL AUTO_INCREMENT,
  `MatchID` varchar(50) NOT NULL,
  `事件类型` varchar(50) NOT NULL,
  `球队ID` int DEFAULT NULL,
  `球员ID` varchar(20) NOT NULL,
  `事件时间` int DEFAULT NULL COMMENT '事件发生时间（比赛第几分钟）',
  PRIMARY KEY (`eventID`),
  KEY `idx_event_match` (`MatchID`),
  KEY `idx_event_team` (`球队ID`),
  KEY `idx_event_player` (`球员ID`),
  KEY `idx_event_type` (`事件类型`),
  CONSTRAINT `fk_event_match` FOREIGN KEY (`MatchID`) REFERENCES `match` (`MatchID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_event_player` FOREIGN KEY (`球员ID`) REFERENCES `player` (`球员ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_event_team` FOREIGN KEY (`球队ID`) REFERENCES `team` (`球队ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `event`
--

LOCK TABLES `event` WRITE;
/*!40000 ALTER TABLE `event` DISABLE KEYS */;
INSERT INTO `event` VALUES (5,'M1001','进球',1,'AI1',14),(6,'M1001','进球',1,'AI1',15),(7,'M1001','进球',1,'AI1',16),(8,'M1001','红牌',2,'DS1',17),(9,'M1001','乌龙球',2,'DS1',21),(11,'M1001','黄牌',2,'DS2',19),(12,'M1002','进球',1,'AI1',23),(13,'M1002','进球',4,'D1',56),(14,'M1002','进球',4,'D2',45),(15,'M1002','黄牌',1,'AI4',42),(16,'M1002','进球',1,'AI1',14),(17,'M1002','红牌',4,'D1',15),(18,'M1002','乌龙球',4,'D2',16),(19,'M1001','红牌',1,'AI2',15),(20,'M1001','红牌',1,'AI2',15),(21,'M1001','进球',1,'AI4',13),(22,'M1001','红牌',2,'DS2',14),(23,'M1001','乌龙球',2,'DS2',15),(24,'M1001','乌龙球',2,'DS4',16),(25,'M1003','进球',3,'G1',11),(26,'M1003','进球',3,'G2',15),(27,'M2001','进球',5,'H5',15),(28,'M2001','进球',6,'W1',16),(30,'M2001','红牌',6,'W5',18),(31,'M2001','进球',5,'H5',50),(32,'M2002','进球',5,'H1',4),(33,'M2002','进球',5,'H1',6),(35,'M2002','红牌',7,'S1',12),(36,'M2002','进球',5,'H2',15),(37,'M2002','乌龙球',7,'S2',75),(38,'M2003','红牌',6,'W6',14),(39,'M2003','黄牌',7,'S2',15),(40,'M2003','进球',6,'W6',14),(41,'M3001','进球',8,'he1',45),(42,'M3001','进球',8,'he3',25),(43,'M3001','进球',9,'Y1',42),(44,'M3001','进球',9,'Y3',56);
/*!40000 ALTER TABLE `event` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_event_insert` AFTER INSERT ON `event` FOR EACH ROW BEGIN
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
        -- 根据事件类型更新相应统计
        CASE NEW.事件类型
            WHEN '进球' THEN
                -- 更新比赛比分
                IF NEW.球队ID = match_home_team THEN
                    UPDATE `match` SET 主队比分 = 主队比分 + 1 WHERE MatchID = NEW.MatchID;
                    -- 更新客队失球数
                    UPDATE team SET 赛事总失球数量 = 赛事总失球数量 + 1 WHERE 球队ID = match_away_team;
                ELSEIF NEW.球队ID = match_away_team THEN
                    UPDATE `match` SET 客队比分 = 客队比分 + 1 WHERE MatchID = NEW.MatchID;
                    -- 更新主队失球数
                    UPDATE team SET 赛事总失球数量 = 赛事总失球数量 + 1 WHERE 球队ID = match_home_team;
                END IF;
                
                -- 更新球队进球数
                UPDATE team SET 赛事总进球数 = 赛事总进球数 + 1 WHERE 球队ID = NEW.球队ID;
                
                -- 更新球队净胜球
                UPDATE team SET 赛事总净胜球 = 赛事总进球数 - 赛事总失球数量 WHERE 球队ID = NEW.球队ID;
                
                -- 更新球员职业生涯进球数
                UPDATE player SET 职业生涯总进球数 = 职业生涯总进球数 + 1 WHERE 球员ID = NEW.球员ID;
                
                -- 更新球员在该赛事的进球数
                UPDATE player_team_history 
                SET 赛事进球数 = 赛事进球数 + 1 
                WHERE 球员ID = NEW.球员ID AND 球队ID = NEW.球队ID AND 赛事ID = match_tournament;
                
            WHEN '乌龙球' THEN
                -- 更新比赛比分（乌龙球给对方加分）
                IF NEW.球队ID = match_home_team THEN
                    UPDATE `match` SET 客队比分 = 客队比分 + 1 WHERE MatchID = NEW.MatchID;
                    -- 更新主队失球数
                    UPDATE team SET 赛事总失球数量 = 赛事总失球数量 + 1 WHERE 球队ID = match_home_team;
                ELSEIF NEW.球队ID = match_away_team THEN
                    UPDATE `match` SET 主队比分 = 主队比分 + 1 WHERE MatchID = NEW.MatchID;
                    -- 更新客队失球数
                    UPDATE team SET 赛事总失球数量 = 赛事总失球数量 + 1 WHERE 球队ID = match_away_team;
                END IF;
                
                -- 更新球队净胜球
                UPDATE team SET 赛事总净胜球 = 赛事总进球数 - 赛事总失球数量 WHERE 球队ID = NEW.球队ID;
                
            WHEN '红牌' THEN
                -- 更新球队红牌数
                UPDATE team SET 赛事红牌数 = 赛事红牌数 + 1 WHERE 球队ID = NEW.球队ID;
                UPDATE player SET 职业生涯总红牌数 = 职业生涯总红牌数 + 1 WHERE 球员ID = NEW.球员ID;
                UPDATE player_team_history SET 赛事红牌数 = 赛事红牌数 + 1 
                WHERE 球员ID = NEW.球员ID AND 球队ID = NEW.球队ID AND 赛事ID = match_tournament;
                
            WHEN '黄牌' THEN
                -- 更新球队黄牌数
                UPDATE team SET 赛事黄牌数 = 赛事黄牌数 + 1 WHERE 球队ID = NEW.球队ID;
                UPDATE player SET 职业生涯总黄牌数 = 职业生涯总黄牌数 + 1 WHERE 球员ID = NEW.球员ID;
                UPDATE player_team_history SET 赛事黄牌数 = 赛事黄牌数 + 1 
                WHERE 球员ID = NEW.球员ID AND 球队ID = NEW.球队ID AND 赛事ID = match_tournament;
        END CASE;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_event_update` AFTER UPDATE ON `event` FOR EACH ROW BEGIN
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
                    -- 回滚客队失球数
                    UPDATE team SET 赛事总失球数量 = GREATEST(赛事总失球数量 - 1, 0) WHERE 球队ID = match_away_team;
                ELSEIF OLD.球队ID = match_away_team THEN
                    UPDATE `match` SET 客队比分 = GREATEST(客队比分 - 1, 0) WHERE MatchID = OLD.MatchID;
                    -- 回滚主队失球数
                    UPDATE team SET 赛事总失球数量 = GREATEST(赛事总失球数量 - 1, 0) WHERE 球队ID = match_home_team;
                END IF;
                
                -- 回滚球队进球数
                UPDATE team SET 赛事总进球数 = GREATEST(赛事总进球数 - 1, 0) WHERE 球队ID = OLD.球队ID;
                
                -- 回滚球队净胜球
                UPDATE team SET 赛事总净胜球 = 赛事总进球数 - 赛事总失球数量 WHERE 球队ID = OLD.球队ID;
                
                -- 回滚球员职业生涯进球数
                UPDATE player SET 职业生涯总进球数 = GREATEST(职业生涯总进球数 - 1, 0) WHERE 球员ID = OLD.球员ID;
                
                -- 回滚球员在该赛事的进球数
                UPDATE player_team_history SET 赛事进球数 = GREATEST(赛事进球数 - 1, 0) 
                WHERE 球员ID = OLD.球员ID AND 球队ID = OLD.球队ID AND 赛事ID = match_tournament;
                
            WHEN '乌龙球' THEN
                -- 回滚比赛比分
                IF OLD.球队ID = match_home_team THEN
                    UPDATE `match` SET 客队比分 = GREATEST(客队比分 - 1, 0) WHERE MatchID = OLD.MatchID;
                    -- 回滚主队失球数
                    UPDATE team SET 赛事总失球数量 = GREATEST(赛事总失球数量 - 1, 0) WHERE 球队ID = match_home_team;
                ELSEIF OLD.球队ID = match_away_team THEN
                    UPDATE `match` SET 主队比分 = GREATEST(主队比分 - 1, 0) WHERE MatchID = OLD.MatchID;
                    -- 回滚客队失球数
                    UPDATE team SET 赛事总失球数量 = GREATEST(赛事总失球数量 - 1, 0) WHERE 球队ID = match_away_team;
                END IF;
                
                -- 回滚球队净胜球
                UPDATE team SET 赛事总净胜球 = 赛事总进球数 - 赛事总失球数量 WHERE 球队ID = OLD.球队ID;
                
            WHEN '红牌' THEN
                -- 回滚球队红牌数
                UPDATE team SET 赛事红牌数 = GREATEST(赛事红牌数 - 1, 0) WHERE 球队ID = OLD.球队ID;
                UPDATE player SET 职业生涯总红牌数 = GREATEST(职业生涯总红牌数 - 1, 0) WHERE 球员ID = OLD.球员ID;
                UPDATE player_team_history SET 赛事红牌数 = GREATEST(赛事红牌数 - 1, 0) 
                WHERE 球员ID = OLD.球员ID AND 球队ID = OLD.球队ID AND 赛事ID = match_tournament;
                
            WHEN '黄牌' THEN
                -- 回滚球队黄牌数
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
                    -- 更新客队失球数
                    UPDATE team SET 赛事总失球数量 = 赛事总失球数量 + 1 WHERE 球队ID = match_away_team;
                ELSEIF NEW.球队ID = match_away_team THEN
                    UPDATE `match` SET 客队比分 = 客队比分 + 1 WHERE MatchID = NEW.MatchID;
                    -- 更新主队失球数
                    UPDATE team SET 赛事总失球数量 = 赛事总失球数量 + 1 WHERE 球队ID = match_home_team;
                END IF;
                
                -- 更新球队进球数
                UPDATE team SET 赛事总进球数 = 赛事总进球数 + 1 WHERE 球队ID = NEW.球队ID;
                
                -- 更新球队净胜球
                UPDATE team SET 赛事总净胜球 = 赛事总进球数 - 赛事总失球数量 WHERE 球队ID = NEW.球队ID;
                
                -- 更新球员职业生涯进球数
                UPDATE player SET 职业生涯总进球数 = 职业生涯总进球数 + 1 WHERE 球员ID = NEW.球员ID;
                
                -- 更新球员在该赛事的进球数
                UPDATE player_team_history 
                SET 赛事进球数 = 赛事进球数 + 1 
                WHERE 球员ID = NEW.球员ID AND 球队ID = NEW.球队ID AND 赛事ID = match_tournament;
                
            WHEN '乌龙球' THEN
                -- 更新比赛比分
                IF NEW.球队ID = match_home_team THEN
                    UPDATE `match` SET 客队比分 = 客队比分 + 1 WHERE MatchID = NEW.MatchID;
                    -- 更新主队失球数
                    UPDATE team SET 赛事总失球数量 = 赛事总失球数量 + 1 WHERE 球队ID = match_home_team;
                ELSEIF NEW.球队ID = match_away_team THEN
                    UPDATE `match` SET 主队比分 = 主队比分 + 1 WHERE MatchID = NEW.MatchID;
                    -- 更新客队失球数
                    UPDATE team SET 赛事总失球数量 = 赛事总失球数量 + 1 WHERE 球队ID = match_away_team;
                END IF;
                
                -- 更新球队净胜球
                UPDATE team SET 赛事总净胜球 = 赛事总进球数 - 赛事总失球数量 WHERE 球队ID = NEW.球队ID;
                
            WHEN '红牌' THEN
                -- 更新球队红牌数
                UPDATE team SET 赛事红牌数 = 赛事红牌数 + 1 WHERE 球队ID = NEW.球队ID;
                UPDATE player SET 职业生涯总红牌数 = 职业生涯总红牌数 + 1 WHERE 球员ID = NEW.球员ID;
                UPDATE player_team_history SET 赛事红牌数 = 赛事红牌数 + 1 
                WHERE 球员ID = NEW.球员ID AND 球队ID = NEW.球队ID AND 赛事ID = match_tournament;
                
            WHEN '黄牌' THEN
                -- 更新球队黄牌数
                UPDATE team SET 赛事黄牌数 = 赛事黄牌数 + 1 WHERE 球队ID = NEW.球队ID;
                UPDATE player SET 职业生涯总黄牌数 = 职业生涯总黄牌数 + 1 WHERE 球员ID = NEW.球员ID;
                UPDATE player_team_history SET 赛事黄牌数 = 赛事黄牌数 + 1 
                WHERE 球员ID = NEW.球员ID AND 球队ID = NEW.球队ID AND 赛事ID = match_tournament;
        END CASE;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_event_delete` AFTER DELETE ON `event` FOR EACH ROW BEGIN
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
                    -- 回滚客队失球数
                    UPDATE team SET 赛事总失球数量 = GREATEST(赛事总失球数量 - 1, 0) WHERE 球队ID = match_away_team;
                ELSEIF OLD.球队ID = match_away_team THEN
                    UPDATE `match` SET 客队比分 = GREATEST(客队比分 - 1, 0) WHERE MatchID = OLD.MatchID;
                    -- 回滚主队失球数
                    UPDATE team SET 赛事总失球数量 = GREATEST(赛事总失球数量 - 1, 0) WHERE 球队ID = match_home_team;
                END IF;
                
                -- 回滚球队进球数
                UPDATE team SET 赛事总进球数 = GREATEST(赛事总进球数 - 1, 0) WHERE 球队ID = OLD.球队ID;
                
                -- 回滚球队净胜球
                UPDATE team SET 赛事总净胜球 = 赛事总进球数 - 赛事总失球数量 WHERE 球队ID = OLD.球队ID;
                
                -- 回滚球员职业生涯进球数
                UPDATE player SET 职业生涯总进球数 = GREATEST(职业生涯总进球数 - 1, 0) WHERE 球员ID = OLD.球员ID;
                
                -- 回滚球员在该赛事的进球数
                UPDATE player_team_history SET 赛事进球数 = GREATEST(赛事进球数 - 1, 0) 
                WHERE 球员ID = OLD.球员ID AND 球队ID = OLD.球队ID AND 赛事ID = match_tournament;
                
            WHEN '乌龙球' THEN
                -- 回滚比赛比分
                IF OLD.球队ID = match_home_team THEN
                    UPDATE `match` SET 客队比分 = GREATEST(客队比分 - 1, 0) WHERE MatchID = OLD.MatchID;
                    -- 回滚主队失球数
                    UPDATE team SET 赛事总失球数量 = GREATEST(赛事总失球数量 - 1, 0) WHERE 球队ID = match_home_team;
                ELSEIF OLD.球队ID = match_away_team THEN
                    UPDATE `match` SET 主队比分 = GREATEST(主队比分 - 1, 0) WHERE MatchID = OLD.MatchID;
                    -- 回滚客队失球数
                    UPDATE team SET 赛事总失球数量 = GREATEST(赛事总失球数量 - 1, 0) WHERE 球队ID = match_away_team;
                END IF;
                
                -- 回滚球队净胜球
                UPDATE team SET 赛事总净胜球 = 赛事总进球数 - 赛事总失球数量 WHERE 球队ID = OLD.球队ID;
                
            WHEN '红牌' THEN
                -- 回滚球队红牌数
                UPDATE team SET 赛事红牌数 = GREATEST(赛事红牌数 - 1, 0) WHERE 球队ID = OLD.球队ID;
                UPDATE player SET 职业生涯总红牌数 = GREATEST(职业生涯总红牌数 - 1, 0) WHERE 球员ID = OLD.球员ID;
                UPDATE player_team_history SET 赛事红牌数 = GREATEST(赛事红牌数 - 1, 0) 
                WHERE 球员ID = OLD.球员ID AND 球队ID = OLD.球队ID AND 赛事ID = match_tournament;
                
            WHEN '黄牌' THEN
                -- 回滚球队黄牌数
                UPDATE team SET 赛事黄牌数 = GREATEST(赛事黄牌数 - 1, 0) WHERE 球队ID = OLD.球队ID;
                UPDATE player SET 职业生涯总黄牌数 = GREATEST(职业生涯总黄牌数 - 1, 0) WHERE 球员ID = OLD.球员ID;
                UPDATE player_team_history SET 赛事黄牌数 = GREATEST(赛事黄牌数 - 1, 0) 
                WHERE 球员ID = OLD.球员ID AND 球队ID = OLD.球队ID AND 赛事ID = match_tournament;
        END CASE;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `match`
--

DROP TABLE IF EXISTS `match`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `match` (
  `MatchID` varchar(50) NOT NULL,
  `比赛名称` varchar(50) NOT NULL,
  `赛事ID` int NOT NULL,
  `小组ID` char(1) DEFAULT NULL,
  `比赛时间` datetime NOT NULL,
  `比赛地点` varchar(50) NOT NULL,
  `主队ID` int DEFAULT NULL,
  `客队ID` int DEFAULT NULL,
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
  CONSTRAINT `fk_match_away_team` FOREIGN KEY (`客队ID`) REFERENCES `team` (`球队ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_match_home_team` FOREIGN KEY (`主队ID`) REFERENCES `team` (`球队ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_match_tournament` FOREIGN KEY (`赛事ID`) REFERENCES `tournament` (`赛事ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `match_chk_1` CHECK ((`比赛状态` in (_utf8mb4'F',_utf8mb4'P')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `match`
--

LOCK TABLES `match` WRITE;
/*!40000 ALTER TABLE `match` DISABLE KEYS */;
INSERT INTO `match` VALUES ('M1001','AI VS DS',1,NULL,'2025-07-31 00:00:00','西操',1,2,7,0,'F',NULL),('M1002','AI VS 地空',1,NULL,'2025-07-31 00:00:00','东操',1,4,3,2,'F',NULL),('M1003','AI VS 工院',1,NULL,'2025-07-30 00:00:00','西操',1,3,0,2,'P',NULL),('M2001','化院 VS 物院 第一轮',2,NULL,'2025-07-31 00:00:00','东操',5,6,2,1,'P',NULL),('M2002','化院 VS 少院 第一轮',2,NULL,'2025-07-31 00:00:00','西操',5,7,4,0,'P',NULL),('M2003','物院 VS 少院 第一轮',2,NULL,'2025-08-07 00:00:00','东操',6,7,1,0,'P',NULL),('M3001','核院 VS 羊村 第一轮',3,NULL,'2025-07-30 00:00:00','西操',8,9,2,2,'P',NULL);
/*!40000 ALTER TABLE `match` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_match_update` AFTER UPDATE ON `match` FOR EACH ROW BEGIN
    DECLARE match_tournament INT DEFAULT NULL;
    DECLARE match_type INT DEFAULT NULL;
    DECLARE home_team_score INT DEFAULT NULL;
    DECLARE away_team_score INT DEFAULT NULL;
    DECLARE home_team_id INT DEFAULT NULL;
    DECLARE away_team_id INT DEFAULT NULL;

    -- 获取比赛信息
    SELECT 赛事ID, 淘汰赛轮次, 主队比分, 客队比分, 主队ID, 客队ID
    INTO match_tournament, match_type, home_team_score, away_team_score, home_team_id, away_team_id
    FROM `match`
    WHERE MatchID = NEW.MatchID;

    -- 检查比赛是否结束
    IF NEW.比赛状态 = 'F' THEN
        -- 检查比赛类型（是否为常规赛）
        IF match_type = 0 THEN
            -- 根据比赛结果更新球队积分
            IF home_team_score > away_team_score THEN
                -- 主队胜利
                UPDATE team SET 赛事积分 = 赛事积分 + 3 WHERE 球队ID = home_team_id;
                UPDATE team SET 赛事积分 = 赛事积分 + 0 WHERE 球队ID = away_team_id;
            ELSEIF home_team_score < away_team_score THEN
                -- 客队胜利
                UPDATE team SET 赛事积分 = 赛事积分 + 0 WHERE 球队ID = home_team_id;
                UPDATE team SET 赛事积分 = 赛事积分 + 3 WHERE 球队ID = away_team_id;
            ELSE
                -- 平局
                UPDATE team SET 赛事积分 = 赛事积分 + 1 WHERE 球队ID = home_team_id;
                UPDATE team SET 赛事积分 = 赛事积分 + 1 WHERE 球队ID = away_team_id;
            END IF;
        END IF;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_update_points_and_ranking_after_match_finish` AFTER UPDATE ON `match` FOR EACH ROW BEGIN
    DECLARE home_points INT DEFAULT 0;
    DECLARE away_points INT DEFAULT 0;

    IF OLD.比赛状态 <> 'F' AND NEW.比赛状态 = 'F' THEN
        IF NEW.主队比分 > NEW.客队比分 THEN
            SET home_points = 3;
            SET away_points = 0;
        ELSEIF NEW.主队比分 < NEW.客队比分 THEN
            SET home_points = 0;
            SET away_points = 3;
        ELSE
            SET home_points = 1;
            SET away_points = 1;
        END IF;

        UPDATE team
        SET 赛事积分 = 赛事积分 + home_points
        WHERE 球队ID = NEW.主队ID;

        UPDATE team
        SET 赛事积分 = 赛事积分 + away_points
        WHERE 球队ID = NEW.客队ID;

        -- 初始化排名变量
        SET @rank := 0;

        -- 正确的排名更新语句
        UPDATE team t
        JOIN (
            SELECT
                球队ID,
                (@rank := @rank + 1) AS new_rank
            FROM team
            WHERE 赛事ID = NEW.赛事ID
            ORDER BY 赛事积分 DESC, 赛事总净胜球 DESC, 赛事总进球数 DESC, 球队ID ASC
        ) ranked
        ON t.球队ID = ranked.球队ID
        SET t.赛事排名 = ranked.new_rank
        WHERE t.赛事ID = NEW.赛事ID;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `player`
--

DROP TABLE IF EXISTS `player`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `player`
--

LOCK TABLES `player` WRITE;
/*!40000 ALTER TABLE `player` DISABLE KEYS */;
INSERT INTO `player` VALUES ('AI1','AI1',5,0,0),('AI2','AI2',0,2,0),('AI3','AI3',0,0,0),('AI4','AI4',1,0,1),('AI5','AI5',0,0,0),('AI6','AI6',0,0,0),('D1','地1',1,1,0),('D2','地2',1,0,0),('D3','地3',0,0,0),('D4','地4',0,0,0),('D5','地5',0,0,0),('D6','地6',0,0,0),('DS1','DS1',0,1,0),('DS2','DS2',0,1,1),('DS3','DS3',0,0,0),('DS4','DS4',0,0,0),('DS5','DS5',0,0,0),('DS6','DS6',0,0,0),('DS7','DS7',0,0,0),('G1','工院1',1,0,0),('G2','工院2',1,0,0),('G3','工院3',0,0,0),('G4','工院4',0,0,0),('G5','工院5',0,0,0),('G6','工院6',0,0,0),('H1','化1',2,0,0),('H2','化2',1,0,0),('H3','化3',0,0,0),('H4','化4',0,0,0),('H5','化5',2,0,0),('H6','化6',0,0,0),('he1','核1',1,0,0),('he2','核2',0,0,0),('he3','核3',1,0,0),('he4','核4',0,0,0),('he5','核5',0,0,0),('he6','核6',0,0,0),('he7','核7',0,0,0),('he8','核8',0,0,0),('S1','少1',0,1,0),('S2','少2',0,0,1),('S3','少3',0,0,0),('S4','少4',0,0,0),('S5','少5',0,0,0),('S6','少6',0,0,0),('W1','物1',1,0,0),('W2','物2',0,0,0),('W3','物3',0,0,0),('W4','物4',0,0,0),('W5','物5',0,1,0),('W6','物6',1,1,0),('Y1','喜羊羊',1,0,0),('Y2','美羊羊',0,0,0),('Y3','沸羊羊',1,0,0),('Y4','懒羊羊',0,0,0),('Y5','暖羊羊',0,0,0),('Y6','慢羊羊',0,0,0),('Y7','灰太狼',0,0,0),('Y8','红太狼',0,0,0);
/*!40000 ALTER TABLE `player` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `player_team_history`
--

DROP TABLE IF EXISTS `player_team_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `player_team_history` (
  `记录ID` int NOT NULL AUTO_INCREMENT,
  `球员ID` varchar(20) NOT NULL,
  `球员号码` int NOT NULL,
  `球队ID` int DEFAULT NULL,
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
  CONSTRAINT `fk_pth_team` FOREIGN KEY (`球队ID`) REFERENCES `team` (`球队ID`) ON DELETE CASCADE,
  CONSTRAINT `fk_pth_tournament` FOREIGN KEY (`赛事ID`) REFERENCES `tournament` (`赛事ID`) ON DELETE CASCADE,
  CONSTRAINT `player_team_history_chk_1` CHECK ((`赛事进球数` >= 0)),
  CONSTRAINT `player_team_history_chk_2` CHECK ((`赛事红牌数` >= 0)),
  CONSTRAINT `player_team_history_chk_3` CHECK ((`赛事黄牌数` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=66 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `player_team_history`
--

LOCK TABLES `player_team_history` WRITE;
/*!40000 ALTER TABLE `player_team_history` DISABLE KEYS */;
INSERT INTO `player_team_history` VALUES (1,'AI1',1,1,1,5,0,0,NULL),(2,'AI2',2,1,1,0,2,0,NULL),(3,'AI3',3,1,1,0,0,0,NULL),(4,'AI4',4,1,1,1,0,1,NULL),(5,'AI5',5,1,1,0,0,0,NULL),(6,'AI6',6,1,1,0,0,0,NULL),(13,'G1',1,3,1,1,0,0,NULL),(14,'G2',2,3,1,1,0,0,NULL),(15,'G3',3,3,1,0,0,0,NULL),(16,'G4',4,3,1,0,0,0,NULL),(17,'G5',5,3,1,0,0,0,NULL),(18,'G6',6,3,1,0,0,0,NULL),(19,'D1',1,4,1,1,1,0,NULL),(20,'D2',2,4,1,1,0,0,NULL),(21,'D3',3,4,1,0,0,0,NULL),(22,'D4',4,4,1,0,0,0,NULL),(23,'D5',5,4,1,0,0,0,NULL),(24,'D6',6,4,1,0,0,0,NULL),(25,'DS1',1,2,1,0,0,0,NULL),(26,'DS2',2,2,1,0,0,0,NULL),(27,'DS3',3,2,1,0,0,0,NULL),(28,'DS4',4,2,1,0,0,0,NULL),(29,'DS5',5,2,1,0,0,0,NULL),(30,'DS6',6,2,1,0,0,0,NULL),(31,'DS7',7,2,1,0,0,0,NULL),(32,'H1',1,5,2,2,0,0,NULL),(33,'H2',2,5,2,1,0,0,NULL),(34,'H3',3,5,2,0,0,0,NULL),(35,'H4',4,5,2,0,0,0,NULL),(36,'H5',5,5,2,2,0,0,NULL),(37,'H6',6,5,2,0,0,0,NULL),(38,'W1',1,6,2,1,0,0,NULL),(39,'W2',2,6,2,0,0,0,NULL),(40,'W3',3,6,2,0,0,0,NULL),(41,'W4',4,6,2,0,0,0,NULL),(42,'W5',5,6,2,0,1,0,NULL),(43,'W6',6,6,2,1,1,0,NULL),(44,'S1',1,7,2,0,1,0,NULL),(45,'S2',2,7,2,0,0,1,NULL),(46,'S3',3,7,2,0,0,0,NULL),(47,'S4',4,7,2,0,0,0,NULL),(48,'S5',5,7,2,0,0,0,NULL),(49,'S6',6,7,2,0,0,0,NULL),(50,'he1',1,8,3,1,0,0,NULL),(51,'he2',2,8,3,0,0,0,NULL),(52,'he3',3,8,3,1,0,0,NULL),(53,'he4',4,8,3,0,0,0,NULL),(54,'he5',5,8,3,0,0,0,NULL),(55,'he6',6,8,3,0,0,0,NULL),(56,'he7',7,8,3,0,0,0,NULL),(57,'he8',8,8,3,0,0,0,NULL),(58,'Y1',1,9,3,1,0,0,NULL),(59,'Y2',2,9,3,0,0,0,NULL),(60,'Y3',3,9,3,1,0,0,NULL),(61,'Y4',4,9,3,0,0,0,NULL),(62,'Y5',5,9,3,0,0,0,NULL),(63,'Y6',6,9,3,0,0,0,NULL),(64,'Y7',7,9,3,0,0,0,NULL),(65,'Y8',8,9,3,0,0,0,NULL);
/*!40000 ALTER TABLE `player_team_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `team`
--

DROP TABLE IF EXISTS `team`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `team` (
  `球队ID` int NOT NULL AUTO_INCREMENT,
  `球队名称` varchar(100) NOT NULL,
  `小组ID` char(1) DEFAULT NULL,
  `赛事ID` int NOT NULL,
  `赛事总进球数` int DEFAULT '0',
  `赛事总失球数量` int DEFAULT '0',
  `赛事总净胜球` int DEFAULT '0',
  `赛事红牌数` int DEFAULT '0',
  `赛事黄牌数` int DEFAULT '0',
  `赛事积分` int DEFAULT '0',
  `赛事排名` int DEFAULT NULL,
  PRIMARY KEY (`球队ID`),
  KEY `idx_team_tournament` (`赛事ID`),
  CONSTRAINT `fk_team_tournament` FOREIGN KEY (`赛事ID`) REFERENCES `tournament` (`赛事ID`) ON DELETE CASCADE,
  CONSTRAINT `team_chk_1` CHECK ((`赛事总进球数` >= 0)),
  CONSTRAINT `team_chk_2` CHECK ((`赛事总失球数量` >= 0)),
  CONSTRAINT `team_chk_3` CHECK ((`赛事红牌数` >= 0)),
  CONSTRAINT `team_chk_4` CHECK ((`赛事黄牌数` >= 0)),
  CONSTRAINT `team_chk_5` CHECK ((`赛事积分` >= 0)),
  CONSTRAINT `team_chk_6` CHECK ((`赛事排名` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `team`
--

LOCK TABLES `team` WRITE;
/*!40000 ALTER TABLE `team` DISABLE KEYS */;
INSERT INTO `team` VALUES (1,'AI',NULL,1,6,4,4,2,1,6,1),(2,'DS',NULL,1,0,7,-7,2,1,0,4),(3,'工院',NULL,1,2,0,2,0,0,0,2),(4,'地空',NULL,1,2,3,-1,1,0,0,3),(5,'化院女足',NULL,2,5,1,4,0,0,0,NULL),(6,'物院女足',NULL,2,2,2,0,2,0,0,NULL),(7,'少院女足',NULL,2,0,5,-4,1,1,0,NULL),(8,'核院1号',NULL,3,2,2,2,0,0,0,NULL),(9,'羊村队',NULL,3,2,2,0,0,0,0,NULL);
/*!40000 ALTER TABLE `team` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tournament`
--

DROP TABLE IF EXISTS `tournament`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
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
PRIMARY KEY (`赛事ID`),
KEY `idx_tournament_competition` (`competition_id`),
KEY `idx_tournament_season` (`season_id`),
CONSTRAINT `fk_tournament_competition` FOREIGN KEY (`competition_id`) REFERENCES `competition` (`competition_id`) ON DELETE CASCADE,
CONSTRAINT `fk_tournament_season` FOREIGN KEY (`season_id`) REFERENCES `season` (`season_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;


-- =============================
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tournament`
--

LOCK TABLES `tournament` WRITE;
/*!40000 ALTER TABLE `tournament` DISABLE KEYS */;
INSERT INTO `tournament` VALUES (1,'冠军杯','2024赛季',0,'2024-01-01 00:00:00','2024-12-31 23:59:59'),(2,'巾帼杯','2024赛季',0,'2024-01-01 00:00:00','2024-12-31 23:59:59'),(3,'八人制比赛','2024赛季',0,'2024-01-01 00:00:00','2024-12-31 23:59:59');
/*!40000 ALTER TABLE `tournament` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
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
  CONSTRAINT `user_chk_1` CHECK ((`状态` in (_utf8mb4'A',_utf8mb4'D')))
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'admin','scrypt:32768:8:1$hashed_password','admin@example.com','admin','2025-07-03 13:10:28',NULL,'A'),(2,'ustc','pbkdf2:sha256:260000$MQZTinQQGBdd1ULB$2a3317be5b8cc9b4fba82686bb6e19eee6f50b3f19fd619b07a4340eb38f4839','2069@qq.com','user','2025-07-03 05:13:05','2025-07-11 08:40:44','A');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'football_management_system'
--

--
-- Dumping routines for database 'football_management_system'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-11 18:45:36
