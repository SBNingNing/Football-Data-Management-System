package com.football.service;

import com.football.dto.PlayerDTO;
import com.football.model.entity.Player;

import java.util.List;

public interface PlayerService {
    List<PlayerDTO> getAllPlayers();
    PlayerDTO getPlayerById(Integer playerId);
    PlayerDTO createPlayer(PlayerDTO playerDTO);
    PlayerDTO updatePlayer(Integer playerId, PlayerDTO playerDTO);
    void deletePlayer(Integer playerId);
    List<PlayerDTO> getPlayersByTeam(Integer teamId);
    List<PlayerDTO> getPlayersBySeason(Integer seasonId);
    List<PlayerDTO> getPlayersByTeamAndSeason(Integer teamId, Integer seasonId);
}
