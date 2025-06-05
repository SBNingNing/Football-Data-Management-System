<template>
  <div class="player-career">
    <!-- 球员基本信息卡片 -->
    <el-card class="player-basic-info">
      <div slot="header" class="clearfix player-name-header">
        <span>{{ player.name }}</span>
      </div>
    </el-card>

    <!-- 球员职业生涯数据 -->
    <el-card class="player-career-stats">
      <div slot="header" class="clearfix">
        <span>球员职业生涯数据</span>
      </div>
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="stat-item" style="background-color: #1e88e5; color: white;">
            <i class="el-icon-finished" style="color: #ffffff; font-size: 40px;"></i>
            <div class="stat-info">
              <div class="stat-number">{{ player.totalGoals }}</div>
              <div class="stat-label">总进球数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item" style="background-color: #1e88e5; color: white;">
            <i class="el-icon-warning" style="color: #ffffff; font-size: 40px;"></i>
            <div class="stat-info">
              <div class="stat-number">{{ player.totalYellowCards }}</div>
              <div class="stat-label">黄牌数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item" style="background-color: #1e88e5; color: white;">
            <i class="el-icon-error" style="color: #ffffff; font-size: 40px;"></i>
            <div class="stat-info">
              <div class="stat-number">{{ player.totalRedCards }}</div>
              <div class="stat-label">红牌数</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 球员赛季表现 -->
    <el-card class="player-seasons">
      <div slot="header" class="clearfix">
        <span>球员赛季表现</span>
      </div>
      <el-collapse v-model="activeSeason">
        <el-collapse-item v-for="season in player.seasons" :key="season.year" :name="season.year">
          <template slot="title">
            <div class="season-title">
              <span>{{ season.year }}</span>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="season-stat">
                <div class="season-label">总进球数</div>
                <div class="season-number">{{ season.totalGoals }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="season-stat">
                <div class="season-label">总黄牌数</div>
                <div class="season-number">{{ season.totalYellowCards }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="season-stat">
                <div class="season-label">总红牌数</div>
                <div class="season-number">{{ season.totalRedCards }}</div>
              </div>
            </el-col>
          </el-row>
          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="24">
              <div v-for="league in season.leagues" :key="league.name" style="margin-bottom: 20px;">
                <h4>{{ league.name }}</h4>
                <el-row :gutter="20">
                  <el-col :span="6">
                    <div class="season-stat">
                      <div class="season-label">球队</div>
                      <div class="season-number">{{ league.team }}</div>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="season-stat">
                      <div class="season-label">进球数</div>
                      <div class="season-number">{{ league.goals }}</div>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="season-stat">
                      <div class="season-label">黄牌数</div>
                      <div class="season-number">{{ league.yellowCards }}</div>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="season-stat">
                      <div class="season-label">红牌数</div>
                      <div class="season-number">{{ league.redCards }}</div>
                    </div>
                  </el-col>
                </el-row>
              </div>
            </el-col>
          </el-row>
        </el-collapse-item>
      </el-collapse>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'PlayerCareer',
  data() {
    return {
      activeSeason: null,
      player: {
        name: '',
        totalGoals: 0,
        totalYellowCards: 0,
        totalRedCards: 0,
        seasons: [],
        currentTeam: '',
        currentTournament: ''
      }
    };
  },
  async mounted() {
    await this.loadPlayerData();
  },
  methods: {
    async loadPlayerData() {
      try {
        // 从路由参数获取球员ID
        const playerId = this.$route.query.playerId || this.$route.params.playerId;
        if (!playerId) {
          this.$message.error('未指定球员ID');
          return;
        }
        
        // 使用后端的获取单个球员信息接口
        const response = await this.$http.get(`/api/players/${playerId}`);
        
        if (response.data.status === 'success') {
          const playerData = response.data.data;
          
          // 适配后端返回的数据结构
          this.player = {
            name: playerData.name,
            studentId: playerData.id,
            currentTeam: playerData.team_name || '暂无队伍',
            currentTournament: playerData.tournament_name || '暂无赛事',
            currentSeason: playerData.season_name || '暂无赛季',
            matchType: playerData.matchType || 'champions-cup',
            playerNumber: playerData.player_number || 0,
            totalGoals: playerData.career_goals || 0,
            totalYellowCards: playerData.career_yellow_cards || 0,
            totalRedCards: playerData.career_red_cards || 0,
            seasons: this.formatSeasonsData(playerData.seasons || [])
          };
        } else {
          this.$message.error(response.data.message || '获取球员数据失败');
        }
      } catch (error) {
        console.error('加载球员数据失败:', error);
        if (error.response && error.response.status === 404) {
          this.$message.error('球员不存在');
        } else {
          this.$message.error('网络错误，无法获取球员数据');
        }
      }
    },

    formatSeasonsData(seasonsData) {
      // 将后端返回的seasons数据格式化为前端需要的格式
      if (!Array.isArray(seasonsData)) {
        console.warn('seasonsData is not an array:', seasonsData);
        return [];
      }

      return seasonsData.map(season => {
        const leagues = [];
        
        try {
          // 遍历该赛季的所有赛事
          const tournaments = season.tournaments || {};
          if (typeof tournaments === 'object' && tournaments !== null) {
            Object.values(tournaments).forEach(tournament => {
              if (tournament && Array.isArray(tournament.teams)) {
                tournament.teams.forEach(team => {
                  if (team) {
                    leagues.push({
                      name: tournament.tournament_name || '未知赛事',
                      team: team.team_name || '未知队伍',
                      goals: Number(team.tournament_goals) || 0,
                      yellowCards: Number(team.tournament_yellow_cards) || 0,
                      redCards: Number(team.tournament_red_cards) || 0
                    });
                  }
                });
              }
            });
          }
        } catch (error) {
          console.error('Error processing tournaments for season:', season, error);
        }

        return {
          year: season.season_name || '未知赛季',
          totalGoals: Number(season.total_goals) || 0,
          totalYellowCards: Number(season.total_yellow_cards) || 0,
          totalRedCards: Number(season.total_red_cards) || 0,
          leagues: leagues
        };
      });
    }
  }
};
</script>

<style scoped>
.player-career {
  max-width: 1200px;
  margin: 0 auto;
}

.player-basic-info,
.player-career-stats,
.player-seasons {
  margin-bottom: 20px;
}

.player-name-header {
  background-color: #1e88e5;
  color: white;
  font-size: 28px;
  font-weight: bold;
  text-align: center;
  padding: 15px 0;
}

.stat-item {
  display: flex;
  align-items: center;
  height: 100px;
  padding: 15px;
  border-radius: 8px;
}

.stat-info {
  display: flex;
  flex-direction: column;
  margin-left: 15px;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
}

.stat-label {
  font-size: 14px;
}

.season-title {
  display: flex;
  align-items: center;
}

.season-stat {
  display: flex;
  flex-direction: column;
}

.season-label {
  font-size: 14px;
  color: #909399;
}

.season-number {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}
</style>