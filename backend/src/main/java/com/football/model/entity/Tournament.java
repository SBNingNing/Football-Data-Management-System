package com.football.model.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.persistence.*;
import java.util.List;

@Entity
@Table(name = "tournament")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Tournament {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "tournament_id")
    private Integer tournamentId;

    @Column(name = "tournament_name", nullable = false)
    private String tournamentName;

    @Column(name = "tournament_type")
    private String tournamentType; // 11人制、8人制等

    @Column(name = "participant_type")
    private String participantType; // 学院、俱乐部等

    @Column(name = "gender_restriction")
    private Character genderRestriction; // 'M' - 男, 'F' - 女, 'U' - 不限

    @OneToMany(mappedBy = "tournament", cascade = CascadeType.ALL)
    private List<Team> teams;

    @OneToMany(mappedBy = "tournament", cascade = CascadeType.ALL)
    private List<Match> matches;
}
