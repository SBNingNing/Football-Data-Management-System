<template>
  <div class="team-info">
    <!-- 球队名称卡片 -->
    <el-card class="team-name-card">
      <div class="team-name-header">
        <div class="back-button-container">
          <el-button 
            type="primary" 
            :icon="ArrowLeft" 
            plain
            @click="goToHomePage"
            class="back-button"
          >
            返回主页
          </el-button>
        </div>
        <h1 class="team-title">{{ team.teamName }}</h1>
      </div>
    </el-card>

    <!-- 球队关键统计数据 -->
    <el-card class="team-stats">
      <template #header>
        <div class="clearfix">
          <span>球队关键统计数据</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="stat-item" style="background-color: #1e88e5; color: white;">
            <el-icon style="color: #ffffff; font-size: 40px;"><Finished /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ team.totalGoals }}</div>
              <div class="stat-label">总进球数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item" style="background-color: #f56c6c; color: white;">
            <el-icon style="color: #ffffff; font-size: 40px;"><Warning /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ team.totalGoalsConceded }}</div>
              <div class="stat-label">总失球数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item" style="background-color: #67c23a; color: white;">
            <el-icon style="color: #ffffff; font-size: 40px;"><Top /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ team.totalGoalDifference }}</div>
              <div class="stat-label">总净胜球</div>
            </div>
          </div>
        </el-col>
      </el-row>
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="8">
          <div class="stat-item" style="background-color: #e6a23c; color: white;">
            <el-icon style="color: #ffffff; font-size: 40px;"><Warning /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ team.totalYellowCards }}</div>
              <div class="stat-label">总黄牌数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item" style="background-color: #f56c6c; color: white;">
            <el-icon style="color: #ffffff; font-size: 40px;"><CircleClose /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ team.totalRedCards }}</div>
              <div class="stat-label">总红牌数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item" style="background-color: #1e88e5; color: white;">
            <el-icon style="color: #ffffff; font-size: 40px;"><Trophy /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ team.bestRank || '暂无' }}</div>
              <div class="stat-label">历史最好排名</div>
            </div>
          </div>
        </el-col>
      </el-row>
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="24">
          <div class="stat-item" style="background-color: #909399; color: white;">
            <el-icon style="color: #ffffff; font-size: 40px;"><Star /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ team.totalPoints }}</div>
              <div class="stat-label">总积分</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 球队参加的比赛信息 -->
    <el-card class="team-matches">
      <template #header>
        <div class="clearfix">
          <span>球队参加的比赛信息</span>
        </div>
      </template>
      <el-collapse v-model="activeSeason">
        <el-collapse-item v-for="record in team.records" :key="record.id" :name="record.id">
          <template slot="title">
            <div class="season-title">
              <span>{{ record.tournamentName }} ({{ getMatchTypeText(record.matchType) }})</span>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :span="4">
              <div class="season-stat">
                <div class="season-label">排名</div>
                <div class="season-number">{{ record.rank || '暂无' }}</div>
              </div>
            </el-col>
            <el-col :span="4">
              <div class="season-stat">
                <div class="season-label">进球数</div>
                <div class="season-number">{{ record.goals }}</div>
              </div>
            </el-col>
            <el-col :span="4">
              <div class="season-stat">
                <div class="season-label">失球数</div>
                <div class="season-number">{{ record.goalsConceded }}</div>
              </div>
            </el-col>
            <el-col :span="4">
              <div class="season-stat">
                <div class="season-label">净胜球</div>
                <div class="season-number">{{ record.goalDifference }}</div>
              </div>
            </el-col>
            <el-col :span="4">
              <div class="season-stat">
                <div class="season-label">积分</div>
                <div class="season-number">{{ record.points }}</div>
              </div>
            </el-col>
            <el-col :span="4">
              <div class="season-stat">
                <div class="season-label">小组</div>
                <div class="season-number">{{ record.group_id || '暂无' }}</div>
              </div>
            </el-col>
          </el-row>
          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="12">
              <div class="season-stat">
                <div class="season-label">黄牌数</div>
                <div class="season-number">{{ record.yellowCards }}</div>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="season-stat">
                <div class="season-label">红牌数</div>
                <div class="season-number">{{ record.redCards }}</div>
              </div>
            </el-col>
          </el-row>
          <el-table :data="record.players" style="width: 100%; margin-top: 20px;">
            <el-table-column prop="number" label="球衣号码" width="100"></el-table-column>
            <el-table-column prop="name" label="球员姓名"></el-table-column>
            <el-table-column prop="playerId" label="球员ID"></el-table-column>
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
import { Finished, Warning, CircleClose, Top, Trophy, Star, ArrowLeft } from '@element-plus/icons-vue'

export default {
  name: 'TeamInfo',
  components: {
    Finished,
    Warning,
    CircleClose,
    Top,
    Trophy,
    Star,
    ArrowLeft
  },
  data() {
    return {
      activeSeason: null,
      team: {
        teamName: '',
        totalGoals: 0,
        totalGoalsConceded: 0,
        totalGoalDifference: 0,
        totalYellowCards: 0,
        totalRedCards: 0,
        totalPoints: 0,
        bestRank: null,
        records: []
      }
    };
  },
  async mounted() {
    await this.loadTeamData();
  },
  methods: {
    async loadTeamData() {
      try {
        // 从路由参数获取球队名称
        const teamName = this.$route.query.teamName || this.$route.params.teamName;
        if (!teamName) {
          this.$message.error('未指定球队名称');
          return;
        }
        
        // 使用后端的获取单个球队信息接口（通过球队名称）
        const response = await this.$http.get(`/api/teams/${encodeURIComponent(teamName)}`);
        
        if (response.data.status === 'success') {
          this.team = response.data.data;
        } else {
          this.$message.error(response.data.message || '获取球队信息失败');
        }
      } catch (error) {
        console.error('获取球队信息失败:', error);
        this.$message.error('获取球队信息失败');
      }
    },
    
    getMatchTypeText(matchType) {
      const matchTypeMap = {
        'champions-cup': '冠军杯',
        'womens-cup': '巾帼杯',
        'eight-a-side': '八人制比赛'
      };
      return matchTypeMap[matchType] || '未知类型';
    },
    
    goToHomePage() {
      this.$router.push('/home')
    }
  }
};
</script>

<style scoped>
.team-info {
  padding: 20px;
}

.team-name-card {
  margin-bottom: 20px;
}

.team-name-header {
  background: linear-gradient(135deg, #1e88e5 0%, #1976d2 100%);
  color: white;
  padding: 30px 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  position: relative;
}

.back-button-container {
  position: absolute;
  top: 20px;
  left: 20px;
}

.back-button {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
  color: white;
}

.back-button:hover {
  background-color: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
  color: white;
}

.team-title {
  font-size: 36px;
  font-weight: bold;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.team-stats, .team-matches {
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-info {
  margin-left: 15px;
  flex-grow: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  margin-top: 5px;
  opacity: 0.9;
}

.season-title {
  font-size: 16px;
  font-weight: bold;
  color: #1e88e5;
}

.season-stat {
  text-align: center;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 10px;
}

.season-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.season-number {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}
</style>