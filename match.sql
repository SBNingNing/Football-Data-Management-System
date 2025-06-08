DROP TRIGGER IF EXISTS trg_update_points_and_ranking_after_match_finish;
DELIMITER $$

CREATE TRIGGER trg_update_points_and_ranking_after_match_finish
AFTER UPDATE ON `match`
FOR EACH ROW
BEGIN
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
END$$

DELIMITER ;
