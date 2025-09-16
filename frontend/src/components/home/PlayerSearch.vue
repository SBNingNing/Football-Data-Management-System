<template>
  <el-card class="player-search-card">
    <template #header>
      <div class="card-header">
        <span>球员搜索</span>
        <div class="search-stats">
          共找到 {{ totalPlayers }} 名球员
        </div>
      </div>
    </template>

    <!-- 搜索区域 -->
    <div class="search-section">
      <el-row :gutter="15">
        <el-col :span="8">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索球员姓名或学号"
            @input="handleSearch"
            clearable
            class="search-input"
          >
            <template #prefix>
              <el-icon><IconSearch /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="6">
          <el-select
            v-model="selectedTeam"
            placeholder="选择队伍"
            @change="handleTeamFilter"
            clearable
            class="team-select"
          >
            <el-option
              v-for="team in teamOptions"
              :key="team"
              :label="team"
              :value="team"
            />
          </el-select>
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
        <el-col :span="4">
          <el-button 
            type="primary" 
            @click="refreshPlayers"
            :loading="loading"
            class="refresh-button"
          >
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 球员列表 -->
    <div class="players-section" v-loading="loading" element-loading-text="正在加载球员数据...">
      <div v-if="filteredPlayers.length === 0 && !loading" class="no-players">
        <el-icon class="no-data-icon"><UserFilled /></el-icon>
        <p>{{ searchKeyword || selectedTeam || selectedMatchType ? '未找到符合条件的球员' : '暂无球员数据' }}</p>
      </div>
      
      <el-row :gutter="20" v-else>
        <el-col 
          :span="8" 
          v-for="player in paginatedPlayers" 
          :key="player.id || player.studentId"
          class="player-col"
        >
          <el-card 
            shadow="hover" 
            class="player-card"
            @click="navigateToPlayerHistory(player)"
          >
            <div class="player-info">
              <div class="player-avatar">
                <el-icon class="avatar-icon"><User /></el-icon>
              </div>
              <div class="player-details">
                <div class="player-name">{{ player.name }}</div>
                <div class="player-meta">
                  <div class="meta-item">
                    <el-icon><CreditCard /></el-icon>
                    <span>{{ player.studentId || player.id }}</span>
                  </div>
                  <!-- 显示所有队伍信息 -->
                  <div class="all-teams" v-if="player.all_teams && player.all_teams.length > 0">
                    <div class="teams-header">
                      <el-icon><Collection /></el-icon>
                      <span>全部队伍 ({{ player.all_teams.length }})</span>
                    </div>
                    <div class="teams-list">
                      <el-tag
                        v-for="(team, index) in player.all_teams.slice(0, 3)"
                        :key="index"
                        :type="getTagType(team.match_type)"
                        size="small"
                        class="team-tag"
                      >
                        {{ team.team_name }}
                        <span v-if="team.player_number">({{ team.player_number }})</span>
                      </el-tag>
                      <el-tag
                        v-if="player.all_teams.length > 3"
                        type="info"
                        size="small"
                        class="more-tag"
                      >
                        +{{ player.all_teams.length - 3 }}
                      </el-tag>
                    </div>
                  </div>
                </div>
                <div class="player-stats">
                  <span class="stat-badge goals">
                    <el-icon><Football /></el-icon>
                    {{ player.career_goals || 0 }}球
                  </span>
                  <span class="stat-badge yellow-cards">
                    <el-icon><Warning /></el-icon>
                    {{ player.career_yellow_cards || 0 }}黄
                  </span>
                  <span class="stat-badge red-cards">
                    <el-icon><CircleClose /></el-icon>
                    {{ player.career_red_cards || 0 }}红
                  </span>
                </div>
              </div>
            </div>
            <div class="player-card-overlay">
              <el-icon><IconView /></el-icon>
              <span>查看详情</span>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper" v-if="filteredPlayers.length > pageSize">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[12, 24, 48, 96]"
        :total="filteredPlayers.length"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handlePageSizeChange"
        @current-change="handleCurrentPageChange"
      />
    </div>
  </el-card>
</template>

<script>
import { 
  Search as IconSearch, 
  Refresh, 
  User, 
  UserFilled, 
  CreditCard, 
  Football, 
  Warning, 
  CircleClose, 
  View as IconView,
  Collection
} from '@element-plus/icons-vue';
import logger from '@/utils/logger.js'
import axios from 'axios';

export default {
  name: 'PlayerSearch',
  components: {
  IconSearch,
    Refresh,
    User,
    UserFilled,
    CreditCard,
    Football,
    Warning,
    CircleClose,
  IconView,
    Collection
  },
  data() {
    return {
      players: [],
      filteredPlayers: [],
      searchKeyword: '',
      selectedTeam: '',
      selectedMatchType: '',
      currentPage: 1,
      pageSize: 12,
      loading: false,
      searchTimer: null,
      totalPlayers: 0,
      teamOptions: []
    };
  },
  computed: {
    paginatedPlayers() {
      const start = (this.currentPage - 1) * this.pageSize;
      const end = start + this.pageSize;
      return this.filteredPlayers.slice(start, end);
    }
  },
  async mounted() {
    await this.fetchPlayers();
  },
  methods: {
    async fetchPlayers() {
      try {
        this.loading = true;
        const response = await axios.get('/api/players');
        const body = response.data;
        // 兼容旧 {status:'success', data:[...]} 与 新 {success:true,data:[...]} 已被 httpClient 的自动解包之外的 axios 直接调用，这里手动解包
        if ((body?.success === true || body?.status === 'success')) {
          const arr = Array.isArray(body.data) ? body.data : Array.isArray(body.records) ? body.records : body.data;
          this.players = Array.isArray(arr)?arr:[];
          logger.info('players fetched', this.players.length);
          
          // 处理球员数据，确保字段一致性
          this.players = this.players.map(player => ({
            ...player,
            studentId: player.studentId || player.id,
            career_goals: player.career_goals || 0,
            career_yellow_cards: player.career_yellow_cards || 0,
            career_red_cards: player.career_red_cards || 0,
            teamName: player.teamName || null,
            number: player.number || null,
            matchType: player.matchType || 'champions-cup',
            all_teams: player.all_teams || []
          }));
          
          // 提取队伍选项（包含所有队伍）
          this.extractTeamOptions();
          // 初始化过滤
          this.filterPlayers();
          
        } else if (Array.isArray(body)) {
          this.players = body;
          this.extractTeamOptions();
          this.filterPlayers();
        } else {
          logger.warn('unexpected players response format', body);
          this.players = [];
        }
      } catch (error) {
  logger.error('fetch players failed', error);
        
        let errorMessage = '获取球员列表失败';
        if (error.response?.status === 404) {
          errorMessage = '球员接口不存在，请检查后端服务';
        } else if (error.response?.status === 500) {
          errorMessage = '服务器内部错误，请稍后重试';
        } else if (error.request) {
          errorMessage = '网络连接失败，请检查网络设置';
        }
        
        this.$message.error(errorMessage);
        this.players = [];
      } finally {
        this.loading = false;
      }
    },

    extractTeamOptions() {
      const teams = new Set();
      this.players.forEach(player => {
        // 只添加所有历史队伍
        if (player.all_teams && Array.isArray(player.all_teams)) {
          player.all_teams.forEach(team => {
            if (team.team_name) {
              teams.add(team.team_name);
            }
          });
        }
      });
      this.teamOptions = Array.from(teams).sort();
  logger.debug('team options', this.teamOptions);
    },

    handleSearch() {
      if (this.searchTimer) {
        clearTimeout(this.searchTimer);
      }
      
      this.searchTimer = setTimeout(() => {
        this.filterPlayers();
      }, 300);
    },

    handleTeamFilter() {
      this.filterPlayers();
    },

    handleMatchTypeFilter() {
      this.filterPlayers();
    },

    filterPlayers() {
      let filtered = [...this.players];
      
      // 按关键词过滤
      if (this.searchKeyword.trim()) {
        const keyword = this.searchKeyword.trim().toLowerCase();
        filtered = filtered.filter(player => 
          (player.name && player.name.toLowerCase().includes(keyword)) ||
          (player.studentId && player.studentId.toString().toLowerCase().includes(keyword)) ||
          (player.id && player.id.toString().toLowerCase().includes(keyword))
        );
      }
      
      // 按队伍过滤（只检查所有历史队伍）
      if (this.selectedTeam) {
        filtered = filtered.filter(player => {
          // 检查所有历史队伍
          if (player.all_teams && Array.isArray(player.all_teams)) {
            return player.all_teams.some(team => team.team_name === this.selectedTeam);
          }
          return false;
        });
      }
      
      // 按赛事类型过滤（只检查所有历史赛事）
      if (this.selectedMatchType) {
        filtered = filtered.filter(player => {
          // 检查所有历史赛事类型
          if (player.all_teams && Array.isArray(player.all_teams)) {
            return player.all_teams.some(team => team.match_type === this.selectedMatchType);
          }
          return false;
        });
      }
      
      this.filteredPlayers = filtered;
      this.totalPlayers = filtered.length;
      this.currentPage = 1;
      
  logger.debug('players filtered count', this.filteredPlayers.length);
    },

    getTagType(matchType) {
      switch (matchType) {
        case 'champions-cup':
          return 'primary';
        case 'womens-cup':
          return 'success';
        case 'eight-a-side':
          return 'warning';
        default:
          return 'info';
      }
    },

    navigateToPlayerHistory(player) {
  logger.info('click player', player);
      
      const playerId = player.id || player.studentId;
      if (!playerId) {
        logger.error('球员ID不存在:', player);
        this.$message.error('球员信息不完整，无法查看详情');
        return;
      }
      
      // 跳转到球员历史页面
      this.$router.push({
        name: 'PlayerHistory',
        query: {
          playerId: playerId
        }
      }).then(() => {
  logger.debug('navigate player detail success');
      }).catch(err => {
  logger.error('navigate player detail failed', err);
        this.$message.error('页面跳转失败');
      });
    },

    async refreshPlayers() {
  logger.info('manual refresh players');
      this.searchKeyword = '';
      this.selectedTeam = '';
      this.selectedMatchType = '';
      await this.fetchPlayers();
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
.player-search-card {
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
.team-select,
.match-type-select {
  width: 100%;
}

.refresh-button {
  width: 100%;
}

.players-section {
  min-height: 400px;
}

.no-players {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.no-data-icon {
  font-size: 48px;
  margin-bottom: 15px;
  color: #e0e0e0;
}

.player-col {
  margin-bottom: 20px;
}

.player-card {
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  min-height: 180px; /* 增加卡片高度以容纳更多信息 */
}

.player-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.player-card:hover .player-card-overlay {
  opacity: 1;
}

.player-info {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  height: 100%;
}

.player-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #409EFF, #36A3FF);
  border-radius: 50%;
  color: white;
  flex-shrink: 0;
}

.avatar-icon {
  font-size: 24px;
}

.player-details {
  flex: 1;
  min-width: 0;
}

.player-name {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.player-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 10px;
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

.player-stats {
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

.stat-badge.goals {
  background-color: #e8f5e8;
  color: #67c23a;
}

.stat-badge.yellow-cards {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.stat-badge.red-cards {
  background-color: #fef0f0;
  color: #f56c6c;
}

.player-card-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(64, 158, 255, 0.9);
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

.player-card-overlay .el-icon {
  font-size: 24px;
}

.pagination-wrapper {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}

.player-number {
  margin-left: 4px;
  color: #909399;
  font-size: 11px;
}

.all-teams {
  margin-top: 4px;
  /* 移除 border-top 因为不再需要分隔线 */
}

.teams-header {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
}

.teams-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.team-tag {
  font-size: 11px;
  height: 20px;
  line-height: 18px;
  padding: 0 6px;
  border-radius: 10px;
}

.more-tag {
  font-size: 11px;
  height: 20px;
  line-height: 18px;
  padding: 0 6px;
  border-radius: 10px;
  cursor: pointer;
}

.more-tag:hover {
  background-color: #c8c9cc;
}
</style>
