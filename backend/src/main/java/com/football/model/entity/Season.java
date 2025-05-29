package com.football.model.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.persistence.*;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "season")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Season {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "season_id")
    private Integer seasonId;

    @Column(name = "season_name", nullable = false)
    private String seasonName;

    @Column(name = "start_time")
    private LocalDateTime startTime;

    @Column(name = "end_time")
    private LocalDateTime endTime;

    @OneToMany(mappedBy = "season", cascade = CascadeType.ALL)
    private List<Team> teams;

    @OneToMany(mappedBy = "season", cascade = CascadeType.ALL)
    private List<Player> players;

    @OneToMany(mappedBy = "season", cascade = CascadeType.ALL)
    private List<Match> matches;

    @OneToMany(mappedBy = "season", cascade = CascadeType.ALL)
    private List<Event> events;
}
