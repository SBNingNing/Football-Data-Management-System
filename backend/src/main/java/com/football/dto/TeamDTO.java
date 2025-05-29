package com.football.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class TeamDTO {
    private Integer teamId;
    private String teamName;
    private Integer tournamentId;
    private String tournamentName;
    private Integer seasonId;
    private String seasonName;
    private Integer seasonGoals;
    private Integer seasonCards;
    private Integer seasonPoints;
    private Integer seasonRank;
    private Integer historicalGoals;
    private Integer historicalCards;
}
