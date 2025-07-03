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
          <el-button 
            type="primary" 
            size="small" 
            @click="refreshTeamData"
            :loading="refreshing"
            style="float: right;"
          >
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
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
          <template #title>
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
            <el-table-column prop="name" label="球员姓名">
              <template #default="scope">
                <div class="player-name-cell">
                  <span 
                    class="clickable-player" 
                    @click="navigateToPlayer(scope.row)"
                    title="点击查看球员详情"
                  >
                    <el-icon class="player-icon"><User /></el-icon>
                    {{ scope.row.name }}
                  </span>
                </div>
              </template>
            </el-table-column>
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
import { useUserStore } from '@/store'
import { Finished, Warning, CircleClose, Top, Trophy, Star, ArrowLeft, User, Refresh } from '@element-plus/icons-vue'

export default {
  name: 'TeamInfo',
  components: {
    Finished,
    Warning,
    CircleClose,
    Top,
    Trophy,
    Star,
    ArrowLeft,
    User,
    Refresh
  },
  data() {
    return {
      activeSeason: null,
      refreshing: false,
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
        // 首先尝试从query参数中获取传递的数据
        const queryTeamData = this.$route.query.teamData;
        if (queryTeamData) {
          try {
            const parsedData = JSON.parse(queryTeamData);
            console.log('从query参数获取的球队数据:', parsedData);
            
            // 使用传递的数据更新组件状态
            this.team = {
              teamName: parsedData.name || parsedData.teamName || '未知球队',
              totalGoals: parsedData.totalGoals || 0,
              totalGoalsConceded: parsedData.totalGoalsConceded || 0,
              totalGoalDifference: (parsedData.totalGoals || 0) - (parsedData.totalGoalsConceded || 0),
              totalYellowCards: parsedData.totalYellowCards || 0,
              totalRedCards: parsedData.totalRedCards || 0,
              totalPoints: parsedData.totalPoints || 0,
              bestRank: parsedData.bestRank || null,
              records: parsedData.records || []
            };
            
            // 如果传递的数据不完整，再从后端获取
            if (!this.team.records || this.team.records.length === 0) {
              console.log('传递的数据不完整，从后端获取完整数据...');
              await this.fetchFromBackend();
            }
            
            return;
          } catch (error) {
            console.error('解析query参数中的球队数据失败:', error);
          }
        }
        
        // 如果没有传递数据或解析失败，从后端获取
        await this.fetchFromBackend();
        
      } catch (error) {
        console.error('加载球队数据异常:', error);
        this.$message.error('加载球队数据失败');
      }
    },
    
    async fetchFromBackend() {
      // 从路由参数或query参数获取球队名称
      const teamName = this.$route.params.teamName || 
                      this.$route.query.teamName || 
                      this.$route.query.name;
      
      console.log('获取到的球队名称:', teamName);
      console.log('当前路由信息:', this.$route);
      
      if (!teamName) {
        this.$message.error('未指定球队名称');
        return;
      }
      
      // 添加loading提示
      const loading = this.$loading({
        lock: true,
        text: '正在加载球队数据...',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)'
      });
      
      try {
        // 直接使用 useUserStore 获取 store 实例
        const store = useUserStore();
        console.log('Store 实例:', store);
        
        // 检查方法是否存在
        if (typeof store.fetchTeamByName !== 'function') {
          console.error('fetchTeamByName 方法不存在，可用方法:', Object.keys(store));
          this.$message.error('系统错误：缺少获取球队数据的方法');
          return;
        }
        
        // 使用 store 中的方法获取球队详情
        const result = await store.fetchTeamByName(teamName);
        
        if (result.success) {
          const teamData = result.data;
          console.log('获取到的球队数据:', teamData);
          
          // 直接使用后端返回的数据结构
          this.team = {
            teamName: teamData.teamName || teamName,
            totalGoals: teamData.totalGoals || 0,
            totalGoalsConceded: teamData.totalGoalsConceded || 0,
            totalGoalDifference: teamData.totalGoalDifference || 0,
            totalYellowCards: teamData.totalYellowCards || 0,
            totalRedCards: teamData.totalRedCards || 0,
            totalPoints: teamData.totalPoints || 0,
            bestRank: teamData.bestRank,
            records: teamData.records || []
          };
          
          // 自动展开第一个记录
          if (this.team.records.length > 0) {
            this.activeSeason = [this.team.records[0].id];
          }
          
          this.$message.success('球队数据加载成功');
        } else {
          this.$message.error(result.error || '获取球队数据失败');
          console.error('获取球队数据失败:', result.error);
        }
      } catch (error) {
        console.error('获取球队数据异常:', error);
        this.$message.error('网络错误，无法获取球队数据');
      } finally {
        loading.close();
      }
    },
    
    async refreshTeamData() {
      this.refreshing = true;
      try {
        await this.fetchFromBackend();
      } finally {
        this.refreshing = false;
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
      // 使用replace而不是push，并强制刷新主页数据
      this.$router.replace('/home').then(() => {
        // 确保路由跳转完成后触发主页数据重载
        this.$nextTick(() => {
          window.dispatchEvent(new Event('resize'));
        });
      }).catch(error => {
        console.error('Navigation error:', error);
        // 如果路由出错，直接跳转
        window.location.href = '/home';
      });
    },
    
    goToPlayerHistory(playerId) {
      if (playerId) {
        this.$router.push({
          name: 'PlayerCareer',
          params: { playerId: playerId },
          query: { playerId: playerId }
        });
      }
    },

    navigateToPlayer(player) {
      console.log('点击了球员:', player);
      
      // 确保有ID数据再跳转
      const playerId = player.id || player.studentId || player.playerId;
      if (!playerId) {
        console.error('球员ID不存在:', player);
        this.$message.error('球员信息不完整，无法查看详情');
        return;
      }
      
      // 跳转到球员历史页面，使用正确的路由名称
      this.$router.push({
        name: 'PlayerHistory', // 确保路由名称正确
        query: {
          playerId: playerId
        }
      }).catch(err => {
        console.error('路由跳转失败:', err);
        this.$message.error('页面跳转失败');
      });
    }
  }
};
</script>

<style scoped>
.team-info {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
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

.player-name-cell {
  display: flex;
  align-items: center;
}

.clickable-player {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #409EFF;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s ease;
  font-weight: 500;
}

.clickable-player:hover {
  color: #ffffff;
  background-color: #409EFF;
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(64, 158, 255, 0.3);
}

.player-icon {
  font-size: 14px;
  transition: transform 0.3s ease;
}

.clickable-player:hover .player-icon {
  transform: scale(1.1);
}

.player-link {
  color: #409EFF;
  text-decoration: none;
}

.player-link:hover {
  color: #66b1ff;
  text-decoration: underline;
}
</style>