<template>
  <div class="competition-history">
    <!-- 赛事基本信息卡片 -->
    <el-card class="competition-basic-info">
      <div slot="header" class="clearfix competition-name-header">
        <span>{{ competition.tournamentName }}</span>
      </div>
      <div class="competition-description">
        <p>{{ competition.description || '暂无描述' }}</p>
      </div>
    </el-card>

    <!-- 赛事历史数据 -->
    <el-card class="competition-history-stats">
      <div slot="header" class="clearfix">
        <span>赛事历史数据</span>
      </div>
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-item" style="background-color: #1e88e5; color: white;">
            <i class="el-icon-finished" style="color: #ffffff; font-size: 40px;"></i>
            <div class="stat-info">
              <div class="stat-number">{{ competition.totalGoals }}</div>
              <div class="stat-label">总进球数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item" style="background-color: #f39c12; color: white;">
            <i class="el-icon-warning" style="color: #ffffff; font-size: 40px;"></i>
            <div class="stat-info">
              <div class="stat-number">{{ competition.totalYellowCards }}</div>
              <div class="stat-label">黄牌数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item" style="background-color: #e74c3c; color: white;">
            <i class="el-icon-error" style="color: #ffffff; font-size: 40px;"></i>
            <div class="stat-info">
              <div class="stat-number">{{ competition.totalRedCards }}</div>
              <div class="stat-label">红牌数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item" style="background-color: #27ae60; color: white;">
            <i class="el-icon-user" style="color: #ffffff; font-size: 40px;"></i>
            <div class="stat-info">
              <div class="stat-number">{{ competition.totalSeasons }}</div>
              <div class="stat-label">赛季数</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 赛事赛季表现 -->
    <el-card class="competition-seasons">
      <div slot="header" class="clearfix">
        <span>赛事赛季表现</span>
      </div>
      <el-collapse v-model="activeSeason">
        <el-collapse-item v-for="season in competition.records" :key="season.id" :name="season.id">
          <template slot="title">
            <div class="season-title">
              <span>{{ season.seasonName }} ({{ season.seasonStartTime ? new Date(season.seasonStartTime).getFullYear() : '' }})</span>
              <span class="season-info">球队数: {{ season.teamCount }} | 总进球: {{ season.totalGoals }}</span>
            </div>
          </template>
          
          <!-- 射手榜 -->
          <el-row :gutter="20" style="margin-bottom: 20px;">
            <el-col :span="24">
              <h4>射手榜</h4>
              <el-table :data="getTopScorers(season)" style="width: 100%" max-height="300">
                <el-table-column prop="player_name" label="球员"></el-table-column>
                <el-table-column prop="team_name" label="球队"></el-table-column>
                <el-table-column prop="player_number" label="球衣号码"></el-table-column>
                <el-table-column prop="goals" label="进球数" sortable></el-table-column>
              </el-table>
            </el-col>
          </el-row>
          
          <!-- 红黄牌榜 -->
          <el-row :gutter="20" style="margin-bottom: 20px;">
            <el-col :span="24">
              <h4>红黄牌榜</h4>
              <el-table :data="getTopCards(season)" style="width: 100%" max-height="300">
                <el-table-column prop="player_name" label="球员"></el-table-column>
                <el-table-column prop="team_name" label="球队"></el-table-column>
                <el-table-column prop="player_number" label="球衣号码"></el-table-column>
                <el-table-column prop="yellowCards" label="黄牌数" sortable></el-table-column>
                <el-table-column prop="redCards" label="红牌数" sortable></el-table-column>
              </el-table>
            </el-col>
          </el-row>
          
          <!-- 赛季积分榜 -->
          <el-row :gutter="20">
            <el-col :span="24">
              <h4>赛季积分榜</h4>
              <el-table :data="season.teams" style="width: 100%">
                <el-table-column prop="rank" label="排名" sortable></el-table-column>
                <el-table-column prop="name" label="球队"></el-table-column>
                <el-table-column prop="points" label="积分" sortable></el-table-column>
                <el-table-column prop="goals" label="进球数" sortable></el-table-column>
                <el-table-column prop="goalsConceded" label="失球数" sortable></el-table-column>
                <el-table-column prop="goalDifference" label="净胜球" sortable></el-table-column>
                <el-table-column prop="yellowCards" label="黄牌数" sortable></el-table-column>
                <el-table-column prop="redCards" label="红牌数" sortable></el-table-column>
                <el-table-column prop="playerCount" label="球员数"></el-table-column>
              </el-table>
            </el-col>
          </el-row>
        </el-collapse-item>
      </el-collapse>
    </el-card>
  </div>
</template>

<script>
import { getTournamentStats } from '@/api/tournaments'

export default {
  name: 'CompetitionHistory',
  data() {
    return {
      activeSeason: null,
      competition: {
        tournamentName: '',
        description: '',
        totalGoals: 0,
        totalYellowCards: 0,
        totalRedCards: 0,
        totalSeasons: 0,
        records: []
      }
    };
  },
  async mounted() {
    await this.loadTournamentData();
  },
  methods: {
    async loadTournamentData() {
      try {
        // 从路由参数获取赛事名称
        const tournamentName = this.$route.params.tournamentName || this.$route.query.tournamentName;
        if (!tournamentName) {
          this.$message.error('缺少赛事名称参数');
          return;
        }
        
        const response = await getTournamentStats(tournamentName);
        
        if (response.data.status === 'success') {
          this.competition = response.data.data;
          this.calculateTotalStats();
        } else {
          this.$message.error(response.data.message || '获取赛事数据失败');
        }
      } catch (error) {
        console.error('加载赛事数据失败:', error);
        this.$message.error('网络错误，无法获取赛事数据');
      }
    },
    
    calculateTotalStats() {
      // 计算总统计数据
      let totalGoals = 0;
      let totalYellowCards = 0;
      let totalRedCards = 0;
      
      this.competition.records.forEach(season => {
        totalGoals += season.totalGoals || 0;
        season.teams.forEach(team => {
          totalYellowCards += team.yellowCards || 0;
          totalRedCards += team.redCards || 0;
        });
      });
      
      this.competition.totalGoals = totalGoals;
      this.competition.totalYellowCards = totalYellowCards;
      this.competition.totalRedCards = totalRedCards;
    },
    
    getTopScorers(season) {
      // 获取射手榜数据
      const allPlayers = [];
      if (season.teams && Array.isArray(season.teams)) {
        season.teams.forEach(team => {
          if (team.players && Array.isArray(team.players)) {
            team.players.forEach(player => {
              if (player.goals > 0) {
                allPlayers.push({
                  ...player,
                  team_name: team.name
                });
              }
            });
          }
        });
      }
      return allPlayers.sort((a, b) => (b.goals || 0) - (a.goals || 0)).slice(0, 10);
    },
    
    getTopCards(season) {
      // 获取红黄牌榜数据
      const allPlayers = [];
      if (season.teams && Array.isArray(season.teams)) {
        season.teams.forEach(team => {
          if (team.players && Array.isArray(team.players)) {
            team.players.forEach(player => {
              if ((player.yellowCards || 0) > 0 || (player.redCards || 0) > 0) {
                allPlayers.push({
                  ...player,
                  team_name: team.name
                });
              }
            });
          }
        });
      }
      return allPlayers.sort((a, b) => 
        ((b.redCards || 0) + (b.yellowCards || 0)) - ((a.redCards || 0) + (a.yellowCards || 0))
      ).slice(0, 10);
    }
  }
};
</script>

<style scoped>
.competition-history {
  max-width: 1200px;
  margin: 0 auto;
}

.competition-basic-info,
.competition-history-stats,
.competition-seasons {
  margin-bottom: 20px;
}

.competition-name-header {
  background-color: #1e88e5;
  color: white;
  font-size: 28px;
  font-weight: bold;
  text-align: center;
  padding: 15px 0;
}

.competition-description {
  text-align: center;
  padding: 20px;
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
  justify-content: space-between;
  width: 100%;
}

.season-info {
  font-size: 12px;
  color: #909399;
  margin-left: 20px;
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