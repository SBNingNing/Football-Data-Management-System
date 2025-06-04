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
        name: '张三',
        totalGoals: 120,
        totalYellowCards: 30,
        totalRedCards: 5,
        seasons: [
          {
            year: '2023',
            totalGoals: 20,
            totalYellowCards: 5,
            totalRedCards: 1,
            leagues: [
              {
                name: '冠军杯',
                team: '红牛队',
                goals: 10,
                yellowCards: 3,
                redCards: 1
              },
              {
                name: '八人制比赛',
                team: '蓝狮队',
                goals: 10,
                yellowCards: 2,
                redCards: 0
              }
            ]
          },
          {
            year: '2022',
            totalGoals: 18,
            totalYellowCards: 4,
            totalRedCards: 0,
            leagues: [
              {
                name: '冠军杯',
                team: '蓝狮队',
                goals: 9,
                yellowCards: 2,
                redCards: 0
              },
              {
                name: '八人制比赛',
                team: '红牛队',
                goals: 9,
                yellowCards: 2,
                redCards: 0
              }
            ]
          }
        ]
      }
    };
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