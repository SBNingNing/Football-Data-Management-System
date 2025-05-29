package com.football.repository;

import com.football.model.entity.Team;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface TeamRepository extends JpaRepository<Team, Integer> {
    List<Team> findByTournamentTournamentId(Integer tournamentId);
    List<Team> findBySeasonSeasonId(Integer seasonId);
    List<Team> findByTournamentTournamentIdAndSeasonSeasonId(Integer tournamentId, Integer seasonId);
}
