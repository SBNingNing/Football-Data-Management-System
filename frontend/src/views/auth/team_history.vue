<template>
  <div class="team-info">
    <!-- 球队名称卡片 -->
    <el-card class="team-name-card">
      <div slot="header" class="clearfix team-name-header">
        <span>{{ team.name }}</span>
      </div>
    </el-card>

    <!-- 球队关键统计数据 -->
    <el-card class="team-stats">
      <div slot="header" class="clearfix">
        <span>球队关键统计数据</span>
      </div>
      <el-row :gutter="20">
        <el-col :span="12">
          <div class="stat-item" style="background-color: #1e88e5; color: white;">
            <i class="el-icon-finished" style="color: #ffffff; font-size: 40px;"></i>
            <div class="stat-info">
              <div class="stat-number">{{ team.totalGoals }}</div>
              <div class="stat-label">总进球数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="stat-item" style="background-color: #1e88e5; color: white;">
            <i class="el-icon-warning" style="color: #ffffff; font-size: 40px;"></i>
            <div class="stat-info">
              <div class="stat-number">黄牌: {{ team.totalYellowCards }} / 红牌: {{ team.totalRedCards }}</div>
              <div class="stat-label">红黄牌数</div>
            </div>
          </div>
        </el-col>
      </el-row>
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="24">
          <div class="stat-item" style="background-color: #1e88e5; color: white;">
            <i class="el-icon-trophy" style="color: #ffffff; font-size: 40px;"></i>
            <div class="stat-info">
              <div class="stat-number">{{ team.bestRank }}</div>
              <div class="stat-label">历史最好排名</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 球队参加的比赛信息 -->
    <el-card class="team-matches">
      <div slot="header" class="clearfix">
        <span>球队参加的比赛信息</span>
      </div>
      <el-collapse v-model="activeSeason">
        <el-collapse-item v-for="season in team.seasons" :key="season.year" :name="season.year">
          <template slot="title">
            <div class="season-title">
              <span>{{ season.year }}</span>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="season-stat">
                <div class="season-label">排名</div>
                <div class="season-number">{{ season.rank }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="season-stat">
                <div class="season-label">进球数</div>
                <div class="season-number">{{ season.goals }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="season-stat">
                <div class="season-label">失球数</div>
                <div class="season-number">{{ season.goalsAgainst }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="season-stat">
                <div class="season-label">净胜球</div>
                <div class="season-number">{{ season.goals - season.goalsAgainst }}</div>
              </div>
            </el-col>
          </el-row>
          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="6">
              <div class="season-stat">
                <div class="season-label">红黄牌数</div>
                <div class="season-number">黄牌: {{ season.yellowCards }} / 红牌: {{ season.redCards }}</div>
              </div>
            </el-col>
          </el-row>
          <el-table :data="season.players" style="width: 100%; margin-top: 20px;">
            <el-table-column prop="name" label="球员姓名"></el-table-column>
            <el-table-column prop="goals" label="进球数"></el-table-column>
            <el-table-column prop="yellowCards" label="黄牌数"></el-table-column>
            <el-table-column prop="redCards" label="红牌数"></el-table-column>
          </el-table>
        </el-collapse-item>
      </el-collapse>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'TeamInfo',
  data() {
    return {
      activeSeason: null,
      team: {
        name: '红牛队',
        totalGoals: 1200,
        totalYellowCards: 300,
        totalRedCards: 20,
        bestRank: 1,
        seasons: [
          {
            year: '2023',
            rank: 1,
            goals: 80,
            goalsAgainst: 30,
            yellowCards: 50,
            redCards: 5,
            players: [
              { name: '张三', goals: 20, yellowCards: 5, redCards: 0 },
              { name: '李四', goals: 10, yellowCards: 3, redCards: 0 },
              { name: '王五', goals: 2, yellowCards: 4, redCards: 1 },
              { name: '赵六', goals: 0, yellowCards: 2, redCards: 0 }
            ]
          },
          {
            year: '2022',
            rank: 2,
            goals: 70,
            goalsAgainst: 35,
            yellowCards: 45,
            redCards: 4,
            players: [
              { name: '张三', goals: 18, yellowCards: 4, redCards: 0 },
              { name: '李四', goals: 9, yellowCards: 3, redCards: 0 },
              { name: '王五', goals: 1, yellowCards: 3, redCards: 1 },
              { name: '赵六', goals: 0, yellowCards: 2, redCards: 0 }
            ]
          }
        ]
      }
    };
  }
};
</script>

<style scoped>
.team-info {
  max-width: 1200px;
  margin: 0 auto;
}

.team-name-card,
.team-stats,
.team-matches {
  margin-bottom: 20px;
}

.team-name-header {
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