package com.football.repository;

import com.football.model.entity.Player;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface PlayerRepository extends JpaRepository<Player, Integer> {
    List<Player> findByTeamTeamId(Integer teamId);
    List<Player> findBySeasonSeasonId(Integer seasonId);
    List<Player> findByTeamTeamIdAndSeasonSeasonId(Integer teamId, Integer seasonId);
}
