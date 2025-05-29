package com.football.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class PlayerDTO {
    private Integer playerId;
    private String playerName;
    private Character gender;
    private Integer teamId;
    private String teamName;
    private Integer seasonId;
    private String seasonName;
    private Integer seasonGoals;
    private Integer seasonCards;
    private Integer historicalGoals;
    private Integer historicalCards;
}
