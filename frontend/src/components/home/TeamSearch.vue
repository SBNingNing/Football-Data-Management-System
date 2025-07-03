<template>
  <el-card class="team-search-card">
    <template #header>
      <div class="card-header">
        <span>球队搜索</span>
        <div class="search-stats">
          共找到 {{ totalTeams }} 支球队
        </div>
      </div>
    </template>

    <!-- 搜索区域 -->
    <div class="search-section">
      <el-row :gutter="15">
        <el-col :span="8">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索球队名称"
            @input="handleSearch"
            clearable
            class="search-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="6">
          <el-select
            v-model="selectedMatchType"
            placeholder="选择赛事类型"
            @change="handleMatchTypeFilter"
            clearable
            class="match-type-select"
          >
            <el-option label="冠军杯" value="champions-cup" />
            <el-option label="巾帼杯" value="womens-cup" />
            <el-option label="八人制" value="eight-a-side" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select
            v-model="selectedTournament"
            placeholder="选择赛事"
            @change="handleTournamentFilter"
            clearable
            class="tournament-select"
          >
            <el-option 
              v-for="tournament in availableTournaments" 
              :key="tournament.id" 
              :label="tournament.name" 
              :value="tournament.id" 
            />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button 
            type="primary" 
            @click="refreshTeams"
            :loading="loading"
            class="refresh-button"
          >
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 球队列表 -->
    <div class="teams-section" v-loading="loading" element-loading-text="正在加载球队数据...">
      <div v-if="filteredTeams.length === 0 && !loading" class="no-teams">
        <el-icon class="no-data-icon"><UserFilled /></el-icon>
        <p>{{ searchKeyword || selectedMatchType || selectedTournament ? '未找到符合条件的球队' : '暂无球队数据' }}</p>
      </div>
      
      <el-row :gutter="20" v-else>
        <el-col 
          :span="8" 
          v-for="team in paginatedTeams" 
          :key="team.id"
          class="team-col"
        >
          <el-card 
            shadow="hover" 
            class="team-card"
            @click="navigateToTeamDetail(team)"
          >
            <div class="team-info">
              <div class="team-avatar">
                <el-icon class="avatar-icon"><Trophy /></el-icon>
              </div>
              <div class="team-details">
                <div class="team-name">{{ team.teamName }}</div>
                <div class="team-meta">
                  <div class="meta-item">
                    <el-icon><Flag /></el-icon>
                    <span>{{ getMatchTypeLabel(team.matchType) }}</span>
                  </div>
                  <div class="meta-item">
                    <el-icon><User /></el-icon>
                    <span>{{ team.players ? team.players.length : 0 }} 名球员</span>
                  </div>
                  <div class="meta-item" v-if="team.tournamentName">
                    <el-icon><Calendar /></el-icon>
                    <span>{{ team.tournamentName }}</span>
                  </div>
                  <div class="meta-item" v-if="team.rank">
                    <el-icon><Trophy /></el-icon>
                    <span>排名: {{ team.rank }}</span>
                  </div>
                </div>
                <div class="team-stats">
                  <span class="stat-badge goals">
                    <el-icon><Football /></el-icon>
                    进球 {{ team.goals || 0 }}
                  </span>
                  <span class="stat-badge points">
                    <el-icon><Medal /></el-icon>
                    积分 {{ team.points || 0 }}
                  </span>
                  <span class="stat-badge cards" v-if="team.yellowCards || team.redCards">
                    <el-icon><Warning /></el-icon>
                    {{ team.yellowCards || 0 }}黄 {{ team.redCards || 0 }}红
                  </span>
                </div>
              </div>
            </div>
            <div class="team-card-overlay">
              <el-icon><View /></el-icon>
              <span>查看详情</span>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper" v-if="filteredTeams.length > pageSize">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[12, 24, 48, 96]"
        :total="filteredTeams.length"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handlePageSizeChange"
        @current-change="handleCurrentPageChange"
      />
    </div>
  </el-card>
</template>

<script>
import { 
  Search, 
  Refresh, 
  User, 
  UserFilled, 
  Trophy, 
  Flag, 
  Calendar, 
  View,
  Close,
  Minus,
  Football,
  Medal,
  Warning
} from '@element-plus/icons-vue';
import axios from 'axios';

export default {
  name: 'TeamSearch',
  components: {
    Search,
    Refresh,
    User,
    UserFilled,
    Trophy,
    Flag,
    Calendar,
    View,
    Close,
    Minus,
    Football,
    Medal,
    Warning
  },
  data() {
    return {
      teams: [],
      filteredTeams: [],
      availableTournaments: [],
      searchKeyword: '',
      selectedMatchType: '',
      selectedTournament: '',
      currentPage: 1,
      pageSize: 12,
      loading: false,
      searchTimer: null,
      totalTeams: 0
    };
  },
  computed: {
    paginatedTeams() {
      const start = (this.currentPage - 1) * this.pageSize;
      const end = start + this.pageSize;
      return this.filteredTeams.slice(start, end);
    }
  },
  async mounted() {
    await this.fetchTeams();
  },
  methods: {
    async fetchTeams() {
      try {
        this.loading = true;
        console.log('开始获取球队数据...');
        
        const response = await axios.get('/api/teams', {
          timeout: 15000,
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
          }
        });
        
        console.log('球队API原始响应:', response.data);
        
        if (response.data?.status === 'success') {
          this.teams = response.data.data || [];
          console.log('成功获取球队数据:', this.teams.length, '支球队');
          
          // 处理球队数据，确保字段一致性和完整性
          this.teams = this.teams.map(team => ({
            ...team,
            // 确保关键字段存在，使用后端返回的字段名
            id: team.id || `team_${Math.random().toString(36).substr(2, 9)}`,
            teamName: team.teamName || team.name || '未知球队',
            matchType: team.matchType || 'champions-cup',
            tournamentId: team.tournamentId || team.tournament_id,
            tournamentName: team.tournamentName || team.tournament_name,
            rank: team.rank || team.tournament_rank,
            goals: team.goals || team.tournament_goals || 0,
            goalsConceded: team.goalsConceded || team.tournament_goals_conceded || 0,
            goalDifference: team.goalDifference || team.tournament_goal_difference || 0,
            points: team.points || team.tournament_points || 0,
            yellowCards: team.yellowCards || team.tournament_yellow_cards || 0,
            redCards: team.redCards || team.tournament_red_cards || 0,
            players: team.players || []
          }));
          
          // 提取可用的赛事列表
          this.extractAvailableTournaments();
          
          console.log('处理后的球队数据:', this.teams);
          
          // 初始化过滤
          this.filterTeams();
          
        } else {
          console.warn('意外的响应格式:', response.data);
          this.teams = [];
        }
      } catch (error) {
        console.error('获取球队列表失败:', error);
        
        let errorMessage = '获取球队列表失败';
        if (error.response?.status === 404) {
          errorMessage = '球队接口不存在，请检查后端服务';
        } else if (error.response?.status === 500) {
          errorMessage = '服务器内部错误，请稍后重试';
        } else if (error.request) {
          errorMessage = '网络连接失败，请检查网络设置';
        }
        
        this.$message.error(errorMessage);
        this.teams = [];
      } finally {
        this.loading = false;
      }
    },

    extractAvailableTournaments() {
      const tournaments = new Map();
      
      this.teams.forEach(team => {
        if (team.tournamentId && team.tournamentName) {
          tournaments.set(team.tournamentId, {
            id: team.tournamentId,
            name: team.tournamentName
          });
        }
      });
      
      this.availableTournaments = Array.from(tournaments.values());
    },

    handleSearch() {
      if (this.searchTimer) {
        clearTimeout(this.searchTimer);
      }
      
      this.searchTimer = setTimeout(() => {
        this.filterTeams();
      }, 300);
    },

    handleMatchTypeFilter() {
      this.filterTeams();
    },

    handleTournamentFilter() {
      this.filterTeams();
    },

    filterTeams() {
      let filtered = [...this.teams];
      
      // 按关键词过滤
      if (this.searchKeyword.trim()) {
        const keyword = this.searchKeyword.trim().toLowerCase();
        filtered = filtered.filter(team => 
          (team.teamName && team.teamName.toLowerCase().includes(keyword)) ||
          (team.id && team.id.toString().toLowerCase().includes(keyword))
        );
      }
      
      // 按赛事类型过滤
      if (this.selectedMatchType) {
        filtered = filtered.filter(team => team.matchType === this.selectedMatchType);
      }
      
      // 按具体赛事过滤
      if (this.selectedTournament) {
        filtered = filtered.filter(team => team.tournamentId === this.selectedTournament);
      }
      
      this.filteredTeams = filtered;
      this.totalTeams = filtered.length;
      this.currentPage = 1;
      
      console.log(`过滤后找到 ${this.filteredTeams.length} 支球队`);
    },

    getMatchTypeLabel(matchType) {
      const labels = {
        'champions-cup': '冠军杯',
        'womens-cup': '巾帼杯',
        'eight-a-side': '八人制'
      };
      return labels[matchType] || matchType;
    },

    navigateToTeamDetail(team) {
      console.log('点击球队:', team);
      
      // 确保球队数据完整性
      if (!team.teamName) {
        console.error('球队信息不完整:', team);
        this.$message.error('球队信息不完整，无法查看详情');
        return;
      }
      
      // 构建传递给team_history的数据
      const teamData = {
        name: team.teamName,
        teamName: team.teamName,
        totalGoals: team.goals || 0,
        totalGoalsConceded: team.goalsConceded || 0,
        totalGoalDifference: team.goalDifference || 0,
        totalYellowCards: team.yellowCards || 0,
        totalRedCards: team.redCards || 0,
        totalPoints: team.points || 0,
        bestRank: team.rank || null,
        records: team.records || []
      };
      
      // 跳转到球队详情页面
      this.$router.push({
        name: 'TeamInfo',
        params: {
          teamName: team.teamName
        },
        query: {
          teamId: team.id,
          matchType: team.matchType,
          tournamentId: team.tournamentId,
          teamData: JSON.stringify(teamData)
        }
      }).then(() => {
        console.log('成功跳转到球队详情页');
      }).catch(err => {
        console.error('路由跳转失败:', err);
        this.$message.error('页面跳转失败，请检查路由配置');
      });
    },

    async refreshTeams() {
      console.log('手动刷新球队数据');
      this.searchKeyword = '';
      this.selectedMatchType = '';
      this.selectedTournament = '';
      await this.fetchTeams();
    },

    handlePageSizeChange(newSize) {
      this.pageSize = newSize;
      this.currentPage = 1;
    },

    handleCurrentPageChange(newPage) {
      this.currentPage = newPage;
    }
  }
};
</script>

<style scoped>
.team-search-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-stats {
  color: #909399;
  font-size: 14px;
}

.search-section {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.search-input,
.match-type-select,
.tournament-select {
  width: 100%;
}

.refresh-button {
  width: 100%;
}

.teams-section {
  min-height: 400px;
}

.no-teams {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.no-data-icon {
  font-size: 48px;
  margin-bottom: 15px;
  color: #e0e0e0;
}

.team-col {
  margin-bottom: 20px;
}

.team-card {
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  min-height: 200px;
}

.team-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.team-card:hover .team-card-overlay {
  opacity: 1;
}

.team-info {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  height: 100%;
}

.team-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  border-radius: 50%;
  color: white;
  flex-shrink: 0;
}

.avatar-icon {
  font-size: 24px;
}

.team-details {
  flex: 1;
  min-width: 0;
}

.team-name {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.team-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #606266;
}

.meta-item .el-icon {
  font-size: 12px;
}

.team-status {
  margin-bottom: 8px;
}

.status-tag {
  font-size: 11px;
}

.team-stats {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.stat-badge {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 2px 6px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.stat-badge.wins {
  background-color: #e8f5e8;
  color: #67c23a;
}

.stat-badge.draws {
  background-color: #f0f9ff;
  color: #409eff;
}

.stat-badge.losses {
  background-color: #fef0f0;
  color: #f56c6c;
}

.stat-badge.goals {
  background-color: #e8f5e8;
  color: #67c23a;
}

.stat-badge.points {
  background-color: #e6f7ff;
  color: #1890ff;
}

.stat-badge.cards {
  background-color: #fff7e6;
  color: #fa8c16;
}

.team-card-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(245, 158, 11, 0.9);
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
  font-weight: 500;
}

.team-card-overlay .el-icon {
  font-size: 24px;
}

.pagination-wrapper {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}
</style>
