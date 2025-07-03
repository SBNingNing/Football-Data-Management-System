<template>
  <div class="player-career">
    <!-- 球员基本信息卡片 -->
    <el-card class="player-basic-info">
      <div class="player-name-header">
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
        <h1 class="player-title">{{ player.name }}</h1>
        <div class="player-meta">
          <span class="meta-item">
            <el-icon><User /></el-icon>
            学号: {{ player.studentId }}
          </span>
          <span class="meta-item" v-if="player.teamHistories && player.teamHistories.length > 0">
            <el-icon><Trophy /></el-icon>
            参与队伍数: {{ player.teamHistories.length }}
          </span>
        </div>
      </div>
    </el-card>

    <!-- 球员队伍历史 -->
    <el-card class="player-team-history" v-if="player.teamHistories && player.teamHistories.length > 0">
      <template #header>
        <div class="clearfix">
          <span>球员队伍历史</span>
        </div>
      </template>
      <el-timeline>
        <el-timeline-item
          v-for="(teamHistory, index) in player.teamHistories"
          :key="index"
          :timestamp="teamHistory.season_name || '未知赛季'"
          placement="top"
        >
          <el-card class="team-history-card">
            <div class="team-info-row">
              <div class="team-detail">
                <h4>{{ teamHistory.team_name || '未知队伍' }}</h4>
                <p class="team-meta">
                  <span class="meta-badge tournament">{{ teamHistory.tournament_name || '未知赛事' }}</span>
                  <span class="meta-badge number" v-if="teamHistory.player_number">
                    球衣号码: {{ teamHistory.player_number }}
                  </span>
                  <span class="meta-badge match-type">{{ getMatchTypeText(teamHistory.matchType) }}</span>
                </p>
              </div>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </el-card>

    <!-- 球员职业生涯数据 -->
    <el-card class="player-career-stats">
      <template #header>
        <div class="clearfix">
          <span>球员职业生涯数据</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="stat-item" style="background-color: #1e88e5; color: white;">
            <el-icon style="color: #ffffff; font-size: 40px;"><Finished /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ player.totalGoals }}</div>
              <div class="stat-label">总进球数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item" style="background-color: #f39c12; color: white;">
            <el-icon style="color: #ffffff; font-size: 40px;"><Warning /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ player.totalYellowCards }}</div>
              <div class="stat-label">黄牌数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item" style="background-color: #e74c3c; color: white;">
            <el-icon style="color: #ffffff; font-size: 40px;"><CircleClose /></el-icon>
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
      <template #header>
        <div class="clearfix">
          <span>球员赛季表现</span>
        </div>
      </template>
      <el-collapse v-model="activeSeason">
        <el-collapse-item v-for="season in player.seasons" :key="season.season_name" :name="season.season_name">
          <template #title>
            <div class="season-title">
              <span>{{ season.season_name }}</span>
              <span class="season-info">总进球: {{ season.total_goals }} | 黄牌: {{ season.total_yellow_cards }} | 红牌: {{ season.total_red_cards }}</span>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="season-stat">
                <div class="season-label">总进球数</div>
                <div class="season-number">{{ season.total_goals }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="season-stat">
                <div class="season-label">总黄牌数</div>
                <div class="season-number">{{ season.total_yellow_cards }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="season-stat">
                <div class="season-label">总红牌数</div>
                <div class="season-number">{{ season.total_red_cards }}</div>
              </div>
            </el-col>
          </el-row>
          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="24">
              <div v-for="(tournament, tournamentName) in season.tournaments" :key="tournamentName" style="margin-bottom: 20px;">
                <h4>{{ tournament.tournament_name }}</h4>
                <div class="tournament-meta">
                  <span class="meta-badge match-type">{{ getMatchTypeText(tournament.match_type) }}</span>
                </div>
                <div v-for="team in tournament.teams" :key="team.team_id" class="team-performance">
                  <el-row :gutter="20">
                    <el-col :span="6">
                      <div class="season-stat">
                        <div class="season-label">球队</div>
                        <div class="season-number">{{ team.team_name }}</div>
                      </div>
                    </el-col>
                    <el-col :span="6">
                      <div class="season-stat">
                        <div class="season-label">球衣号码</div>
                        <div class="season-number">{{ team.player_number || '-' }}</div>
                      </div>
                    </el-col>
                    <el-col :span="6">
                      <div class="season-stat">
                        <div class="season-label">进球数</div>
                        <div class="season-number">{{ team.tournament_goals }}</div>
                      </div>
                    </el-col>
                    <el-col :span="6">
                      <div class="season-stat">
                        <div class="season-label">黄牌数</div>
                        <div class="season-number">{{ team.tournament_yellow_cards }}</div>
                      </div>
                    </el-col>
                  </el-row>
                  <el-row :gutter="20" style="margin-top: 10px;">
                    <el-col :span="6">
                      <div class="season-stat">
                        <div class="season-label">红牌数</div>
                        <div class="season-number">{{ team.tournament_red_cards }}</div>
                      </div>
                    </el-col>
                  </el-row>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-collapse-item>
      </el-collapse>
    </el-card>
  </div>
</template>

<script>
import { useUserStore } from '@/store'
import { Finished, Warning, CircleClose, User, Trophy, ArrowLeft } from '@element-plus/icons-vue'

export default {
  name: 'PlayerCareer',
  components: {
    Finished,
    Warning,
    CircleClose,
    User,
    Trophy,
    ArrowLeft
  },
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
        currentTournament: '',
        studentId: '',
        teamHistories: [] // 新增：队伍历史记录
      },
      store: null
    };
  },
  async mounted() {
    this.store = useUserStore();
    await this.loadPlayerData();
  },
  methods: {
    async loadPlayerData() {
      try {
        // 从路由参数或query参数获取球员ID
        const playerId = this.$route.params.playerId || 
                        this.$route.query.playerId || 
                        this.playerId; // 来自props
        
        console.log('获取到的球员ID:', playerId);
        console.log('当前路由信息:', this.$route);
        
        if (!playerId) {
          this.$message.error('未指定球员ID');
          return;
        }
        
        // 添加loading提示
        const loading = this.$loading({
          lock: true,
          text: '正在加载球员数据...',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        });
        
        // 使用 store 中的方法获取球员详情
        const result = await this.store.fetchPlayerById(playerId);
        
        loading.close();
        
        if (result.success) {
          const playerData = result.data;
          console.log('获取到的球员数据:', playerData);
          
          // 适配后端返回的数据结构
          this.player = {
            name: playerData.name || '未知球员',
            studentId: playerData.id,
            currentTeam: playerData.team_name || '暂无队伍',
            currentTournament: playerData.tournament_name || '暂无赛事',
            currentSeason: playerData.season_name || '暂无赛季',
            matchType: playerData.matchType || 'champions-cup',
            playerNumber: playerData.player_number || 0,
            totalGoals: playerData.career_goals || 0,
            totalYellowCards: playerData.career_yellow_cards || 0,
            totalRedCards: playerData.career_red_cards || 0,
            seasons: playerData.seasons || [], // 直接使用后端返回的赛季数据
            teamHistories: playerData.team_histories || [] // 新增：处理队伍历史记录
          };
          
          // 自动展开第一个赛季
          if (this.player.seasons.length > 0) {
            this.activeSeason = [this.player.seasons[0].season_name];
          }
          
          this.$message.success('球员数据加载成功');
        } else {
          this.$message.error(result.error || '获取球员数据失败');
          console.error('获取球员数据失败:', result.error);
        }
      } catch (error) {
        console.error('加载球员数据异常:', error);
        this.$message.error('网络错误，无法获取球员数据');
      }
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

    getMatchTypeText(matchType) {
      const matchTypeMap = {
        'champions-cup': '冠军杯',
        'womens-cup': '巾帼杯',
        'eight-a-side': '八人制'
      };
      return matchTypeMap[matchType] || '未知赛事类型';
    },
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
  background: linear-gradient(135deg, #1e88e5 0%, #1976d2 100%);
  color: white;
  padding: 30px 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(30, 136, 229, 0.3);
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

.player-title {
  font-size: 36px;
  font-weight: bold;
  margin: 0 0 15px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.player-meta {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-top: 15px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
  opacity: 0.9;
}

.meta-item i {
  font-size: 18px;
}

.stat-item {
  display: flex;
  align-items: center;
  height: 100px;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
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

.player-team-history {
  margin-bottom: 20px;
}

.team-history-card {
  margin-bottom: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.team-info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.team-detail h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.team-meta {
  margin: 0;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.meta-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.meta-badge.tournament {
  background-color: #e3f2fd;
  color: #1976d2;
}

.meta-badge.number {
  background-color: #f3e5f5;
  color: #7b1fa2;
}

.meta-badge.match-type {
  background-color: #e8f5e8;
  color: #388e3c;
}

.el-timeline {
  padding-left: 20px;
}

.el-timeline-item {
  padding-bottom: 20px;
}

.tournament-meta {
  margin-bottom: 10px;
}

.team-performance {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 10px;
  border-left: 4px solid #409eff;
}

.team-performance:last-child {
  margin-bottom: 0;
}
</style>