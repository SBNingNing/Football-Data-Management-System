<template>
  <div class="competition-history">
    <!-- 赛事基本信息卡片 -->
    <el-card class="competition-basic-info">
      <div slot="header" class="clearfix competition-name-header">
        <span>{{ competition.name }}</span>
      </div>
      <div class="competition-description">
        <p>{{ competition.description }}</p>
      </div>
    </el-card>

    <!-- 赛事历史数据 -->
    <el-card class="competition-history-stats">
      <div slot="header" class="clearfix">
        <span>赛事历史数据</span>
      </div>
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="stat-item" style="background-color: #1e88e5; color: white;">
            <i class="el-icon-finished" style="color: #ffffff; font-size: 40px;"></i>
            <div class="stat-info">
              <div class="stat-number">{{ competition.totalGoals }}</div>
              <div class="stat-label">总进球数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item" style="background-color: #1e88e5; color: white;">
            <i class="el-icon-warning" style="color: #ffffff; font-size: 40px;"></i>
            <div class="stat-info">
              <div class="stat-number">{{ competition.totalYellowCards }}</div>
              <div class="stat-label">黄牌数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item" style="background-color: #1e88e5; color: white;">
            <i class="el-icon-error" style="color: #ffffff; font-size: 40px;"></i>
            <div class="stat-info">
              <div class="stat-number">{{ competition.totalRedCards }}</div>
              <div class="stat-label">红牌数</div>
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
        <el-collapse-item v-for="season in competition.seasons" :key="season.year" :name="season.year">
          <template slot="title">
            <div class="season-title">
              <span>{{ season.year }}</span>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :span="24">
              <div class="season-stat">
                <div class="season-label">四强球队</div>
                <div class="season-number">{{ season.topFourTeams.join(', ') }}</div>
              </div>
            </el-col>
          </el-row>
          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="24">
              <h4>射手榜</h4>
              <el-table :data="season.topScorers" style="width: 100%">
                <el-table-column prop="player" label="球员"></el-table-column>
                <el-table-column prop="team" label="球队"></el-table-column>
                <el-table-column prop="goals" label="进球数"></el-table-column>
              </el-table>
            </el-col>
          </el-row>
          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="24">
              <h4>红黄牌榜</h4>
              <el-table :data="season.topCards" style="width: 100%">
                <el-table-column prop="player" label="球员"></el-table-column>
                <el-table-column prop="team" label="球队"></el-table-column>
                <el-table-column prop="yellowCards" label="黄牌数"></el-table-column>
                <el-table-column prop="redCards" label="红牌数"></el-table-column>
              </el-table>
            </el-col>
          </el-row>
          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="24">
              <h4>赛季积分榜</h4>
              <el-table :data="season.standings" style="width: 100%">
                <el-table-column prop="rank" label="排名"></el-table-column>
                <el-table-column prop="team" label="球队"></el-table-column>
                <el-table-column prop="points" label="积分"></el-table-column>
                <el-table-column prop="goalsFor" label="进球数"></el-table-column>
                <el-table-column prop="goalsAgainst" label="失球数"></el-table-column>
                <el-table-column label="净胜球">
                  <template slot-scope="scope">
                    {{ scope.row.goalsFor - scope.row.goalsAgainst }}
                  </template>
                </el-table-column>
                <el-table-column prop="yellowCards" label="黄牌数"></el-table-column>
                <el-table-column prop="redCards" label="红牌数"></el-table-column>
              </el-table>
            </el-col>
          </el-row>
        </el-collapse-item>
      </el-collapse>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'CompetitionHistory',
  data() {
    return {
      activeSeason: null,
      competition: {
        name: '冠军杯',
        description: '冠军杯是最高水平的足球赛事，吸引了众多顶级球队参与。',
        totalGoals: 1200,
        totalYellowCards: 300,
        totalRedCards: 50,
        seasons: [
          {
            year: '2023',
            topFourTeams: ['红牛队', '蓝狮队', '雄鹰队', '猛虎队'],
            topScorers: [
              { player: '张三', team: '红牛队', goals: 20 },
              { player: '李四', team: '蓝狮队', goals: 18 },
              { player: '王五', team: '雄鹰队', goals: 15 },
              { player: '赵六', team: '猛虎队', goals: 12 }
            ],
            topCards: [
              { player: '孙八', team: '狂狼队', yellowCards: 8, redCards: 2 },
              { player: '周九', team: '红牛队', yellowCards: 6, redCards: 1 },
              { player: '吴十', team: '蓝狮队', yellowCards: 5, redCards: 1 },
              { player: '郑一', team: '雄鹰队', yellowCards: 4, redCards: 0 }
            ],
            standings: [
              { rank: 1, team: '红牛队', points: 30, goalsFor: 80, goalsAgainst: 20, yellowCards: 10, redCards: 2 },
              { rank: 2, team: '蓝狮队', points: 28, goalsFor: 75, goalsAgainst: 25, yellowCards: 12, redCards: 1 },
              { rank: 3, team: '雄鹰队', points: 25, goalsFor: 70, goalsAgainst: 30, yellowCards: 15, redCards: 0 },
              { rank: 4, team: '猛虎队', points: 22, goalsFor: 65, goalsAgainst: 35, yellowCards: 18, redCards: 1 },
              { rank: 5, team: '飞豹队', points: 18, goalsFor: 60, goalsAgainst: 40, yellowCards: 20, redCards: 0 }
            ]
          },
          {
            year: '2022',
            topFourTeams: ['蓝狮队', '红牛队', '飞豹队', '狂狼队'],
            topScorers: [
              { player: '小红', team: '蓝狮队', goals: 18 },
              { player: '小芳', team: '红牛队', goals: 16 },
              { player: '小丽', team: '飞豹队', goals: 14 },
              { player: '小美', team: '狂狼队', goals: 12 }
            ],
            topCards: [
              { player: '小华', team: '鸿雁队', yellowCards: 7, redCards: 2 },
              { player: '小玲', team: '蓝狮队', yellowCards: 5, redCards: 1 },
              { player: '小燕', team: '红牛队', yellowCards: 4, redCards: 1 },
              { player: '小雪', team: '飞豹队', yellowCards: 3, redCards: 0 }
            ],
            standings: [
              { rank: 1, team: '蓝狮队', points: 32, goalsFor: 85, goalsAgainst: 22, yellowCards: 11, redCards: 1 },
              { rank: 2, team: '红牛队', points: 30, goalsFor: 80, goalsAgainst: 25, yellowCards: 13, redCards: 2 },
              { rank: 3, team: '飞豹队', points: 26, goalsFor: 75, goalsAgainst: 30, yellowCards: 14, redCards: 1 },
              { rank: 4, team: '狂狼队', points: 24, goalsFor: 70, goalsAgainst: 35, yellowCards: 16, redCards: 1 },
              { rank: 5, team: '雄鹰队', points: 20, goalsFor: 65, goalsAgainst: 40, yellowCards: 17, redCards: 0 }
            ]
          }
        ]
      }
    };
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