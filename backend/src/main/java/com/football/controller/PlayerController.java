package com.football.controller;

import com.football.dto.PlayerDTO;
import com.football.service.PlayerService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

@RestController
@RequestMapping("/api/players")
@CrossOrigin(origins = "http://localhost:8081")
public class PlayerController {

    @Autowired
    private PlayerService playerService;

    @GetMapping
    public ResponseEntity<List<PlayerDTO>> getAllPlayers() {
        return ResponseEntity.ok(playerService.getAllPlayers());
    }

    @GetMapping("/{id}")
    public ResponseEntity<PlayerDTO> getPlayerById(@PathVariable("id") Integer id) {
        return ResponseEntity.ok(playerService.getPlayerById(id));
    }

    @PostMapping
    @PreAuthorize("hasRole('ADMIN') or hasRole('RECORDER')")
    public ResponseEntity<PlayerDTO> createPlayer(@Valid @RequestBody PlayerDTO playerDTO) {
        return ResponseEntity.ok(playerService.createPlayer(playerDTO));
    }

    @PutMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN') or hasRole('RECORDER')")
    public ResponseEntity<PlayerDTO> updatePlayer(@PathVariable("id") Integer id, @Valid @RequestBody PlayerDTO playerDTO) {
        return ResponseEntity.ok(playerService.updatePlayer(id, playerDTO));
    }

    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Void> deletePlayer(@PathVariable("id") Integer id) {
        playerService.deletePlayer(id);
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/team/{teamId}")
    public ResponseEntity<List<PlayerDTO>> getPlayersByTeam(@PathVariable("teamId") Integer teamId) {
        return ResponseEntity.ok(playerService.getPlayersByTeam(teamId));
    }

    @GetMapping("/season/{seasonId}")
    public ResponseEntity<List<PlayerDTO>> getPlayersBySeason(@PathVariable("seasonId") Integer seasonId) {
        return ResponseEntity.ok(playerService.getPlayersBySeason(seasonId));
    }

    @GetMapping("/team/{teamId}/season/{seasonId}")
    public ResponseEntity<List<PlayerDTO>> getPlayersByTeamAndSeason(
            @PathVariable("teamId") Integer teamId,
            @PathVariable("seasonId") Integer seasonId) {
        return ResponseEntity.ok(playerService.getPlayersByTeamAndSeason(teamId, seasonId));
    }
}
