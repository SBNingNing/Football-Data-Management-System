package com.football.model.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.persistence.*;

@Entity
@Table(name = "player")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Player {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "player_id")
    private Integer playerId;

    @Column(name = "player_name", nullable = false)
    private String playerName;

    @Column(name = "gender", nullable = false)
    private Character gender;

    @ManyToOne
    @JoinColumn(name = "team_id")
    private Team team;

    @ManyToOne
    @JoinColumn(name = "season_id")
    private Season season;

    @Column(name = "season_goals")
    private Integer seasonGoals = 0;

    @Column(name = "season_cards")
    private Integer seasonCards = 0;

    @Column(name = "historical_goals")
    private Integer historicalGoals = 0;

    @Column(name = "historical_cards")
    private Integer historicalCards = 0;
}
