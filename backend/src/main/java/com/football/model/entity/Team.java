package com.football.model.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.persistence.*;
import java.util.List;

@Entity
@Table(name = "team")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Team {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "team_id")
    private Integer teamId;

    @Column(name = "team_name", nullable = false)
    private String teamName;

    @ManyToOne
    @JoinColumn(name = "tournament_id")
    private Tournament tournament;

    @ManyToOne
    @JoinColumn(name = "season_id")
    private Season season;

    @Column(name = "season_goals")
    private Integer seasonGoals = 0;

    @Column(name = "season_cards")
    private Integer seasonCards = 0;

    @Column(name = "season_points")
    private Integer seasonPoints = 0;

    @Column(name = "season_rank")
    private Integer seasonRank;

    @Column(name = "historical_goals")
    private Integer historicalGoals = 0;

    @Column(name = "historical_cards")
    private Integer historicalCards = 0;

    @OneToMany(mappedBy = "team", cascade = CascadeType.ALL)
    private List<Player> players;
}
