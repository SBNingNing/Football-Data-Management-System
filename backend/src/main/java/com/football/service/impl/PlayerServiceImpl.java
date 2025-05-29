package com.football.service.impl;

import com.football.dto.PlayerDTO;
import com.football.exception.ResourceNotFoundException;
import com.football.model.entity.Player;
import com.football.model.entity.Season;
import com.football.model.entity.Team;
import com.football.repository.PlayerRepository;
import com.football.repository.SeasonRepository;
import com.football.repository.TeamRepository;
import com.football.service.PlayerService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class PlayerServiceImpl implements PlayerService {

    @Autowired
    private PlayerRepository playerRepository;

    @Autowired
    private TeamRepository teamRepository;

    @Autowired
    private SeasonRepository seasonRepository;

    @Override
    public List<PlayerDTO> getAllPlayers() {
        return playerRepository.findAll().stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    @Override
    public PlayerDTO getPlayerById(Integer playerId) {
        Player player = playerRepository.findById(playerId)
                .orElseThrow(() -> new ResourceNotFoundException("Player not found with id " + playerId));
        return convertToDTO(player);
    }

    @Override
    public PlayerDTO createPlayer(PlayerDTO playerDTO) {
        Player player = convertToEntity(playerDTO);
        Player savedPlayer = playerRepository.save(player);
        return convertToDTO(savedPlayer);
    }

    @Override
    public PlayerDTO updatePlayer(Integer playerId, PlayerDTO playerDTO) {
        Player existingPlayer = playerRepository.findById(playerId)
                .orElseThrow(() -> new ResourceNotFoundException("Player not found with id " + playerId));
        
        existingPlayer.setPlayerName(playerDTO.getPlayerName());
        existingPlayer.setGender(playerDTO.getGender());
        
        if (playerDTO.getTeamId() != null) {
            Team team = teamRepository.findById(playerDTO.getTeamId())
                    .orElseThrow(() -> new ResourceNotFoundException("Team not found with id " + playerDTO.getTeamId()));
            existingPlayer.setTeam(team);
        }
        
        if (playerDTO.getSeasonId() != null) {
            Season season = seasonRepository.findById(playerDTO.getSeasonId())
                    .orElseThrow(() -> new ResourceNotFoundException("Season not found with id " + playerDTO.getSeasonId()));
            existingPlayer.setSeason(season);
        }
        
        existingPlayer.setSeasonGoals(playerDTO.getSeasonGoals());
        existingPlayer.setSeasonCards(playerDTO.getSeasonCards());
        existingPlayer.setHistoricalGoals(playerDTO.getHistoricalGoals());
        existingPlayer.setHistoricalCards(playerDTO.getHistoricalCards());
        
        Player updatedPlayer = playerRepository.save(existingPlayer);
        return convertToDTO(updatedPlayer);
    }

    @Override
    public void deletePlayer(Integer playerId) {
        Player player = playerRepository.findById(playerId)
                .orElseThrow(() -> new ResourceNotFoundException("Player not found with id " + playerId));
        playerRepository.delete(player);
    }

    @Override
    public List<PlayerDTO> getPlayersByTeam(Integer teamId) {
        return playerRepository.findByTeamTeamId(teamId).stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    @Override
    public List<PlayerDTO> getPlayersBySeason(Integer seasonId) {
        return playerRepository.findBySeasonSeasonId(seasonId).stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    @Override
    public List<PlayerDTO> getPlayersByTeamAndSeason(Integer teamId, Integer seasonId) {
        return playerRepository.findByTeamTeamIdAndSeasonSeasonId(teamId, seasonId).stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    private PlayerDTO convertToDTO(Player player) {
        PlayerDTO dto = new PlayerDTO();
        dto.setPlayerId(player.getPlayerId());
        dto.setPlayerName(player.getPlayerName());
        dto.setGender(player.getGender());
        
        if (player.getTeam() != null) {
            dto.setTeamId(player.getTeam().getTeamId());
            dto.setTeamName(player.getTeam().getTeamName());
        }
        
        if (player.getSeason() != null) {
            dto.setSeasonId(player.getSeason().getSeasonId());
            dto.setSeasonName(player.getSeason().getSeasonName());
        }
        
        dto.setSeasonGoals(player.getSeasonGoals());
        dto.setSeasonCards(player.getSeasonCards());
        dto.setHistoricalGoals(player.getHistoricalGoals());
        dto.setHistoricalCards(player.getHistoricalCards());
        
        return dto;
    }

    private Player convertToEntity(PlayerDTO playerDTO) {
        Player player = new Player();
        player.setPlayerId(playerDTO.getPlayerId());
        player.setPlayerName(playerDTO.getPlayerName());
        player.setGender(playerDTO.getGender());
        
        if (playerDTO.getTeamId() != null) {
            Team team = teamRepository.findById(playerDTO.getTeamId())
                    .orElseThrow(() -> new ResourceNotFoundException("Team not found with id " + playerDTO.getTeamId()));
            player.setTeam(team);
        }
        
        if (playerDTO.getSeasonId() != null) {
            Season season = seasonRepository.findById(playerDTO.getSeasonId())
                    .orElseThrow(() -> new ResourceNotFoundException("Season not found with id " + playerDTO.getSeasonId()));
            player.setSeason(season);
        }
        
        player.setSeasonGoals(playerDTO.getSeasonGoals());
        player.setSeasonCards(playerDTO.getSeasonCards());
        player.setHistoricalGoals(playerDTO.getHistoricalGoals());
        player.setHistoricalCards(playerDTO.getHistoricalCards());
        
        return player;
    }
}
