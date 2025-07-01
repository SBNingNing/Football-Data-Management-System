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
              <el-icon><Search /></el-icon>
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
                  <div class="meta-item" v-if="player.teamName">
                    <el-icon><Trophy /></el-icon>
                    <span>{{ player.teamName }}</span>
                  </div>
                  <div class="meta-item" v-if="player.number">
                    <el-icon><Tickets /></el-icon>
                    <span>{{ player.number }}号</span>
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
              <el-icon><View /></el-icon>
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
  Search, 
  Refresh, 
  User, 
  UserFilled, 
  CreditCard, 
  Trophy, 
  Tickets, 
  Football, 
  Warning, 
  CircleClose, 
  View 
} from '@element-plus/icons-vue';
import axios from 'axios';

export default {
  name: 'PlayerSearch',
  components: {
    Search,
    Refresh,
    User,
    UserFilled,
    CreditCard,
    Trophy,
    Tickets,
    Football,
    Warning,
    CircleClose,
    View
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
      if (this.loading) return;
      
      this.loading = true;
      console.log('开始获取球员数据...');
      
      try {
        const response = await axios.get('/api/players', {
          timeout: 15000,
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
          }
        });
        
        console.log('球员API响应:', response.data);
        
        if (response.data?.status === 'success') {
          this.players = response.data.data || [];
          this.filteredPlayers = [...this.players];
          this.totalPlayers = this.players.length;
          
          // 提取队伍选项
          this.extractTeamOptions();
          
          console.log(`成功加载 ${this.players.length} 名球员`);
          this.$message.success(`成功加载 ${this.players.length} 名球员`);
        } else {
          console.error('球员API返回错误:', response.data?.message);
          this.$message.error(response.data?.message || '获取球员数据失败');
          this.players = [];
          this.filteredPlayers = [];
          this.totalPlayers = 0;
        }
      } catch (error) {
        console.error('获取球员数据失败:', error);
        this.$message.error('网络错误，无法获取球员数据');
        this.players = [];
        this.filteredPlayers = [];
        this.totalPlayers = 0;
      } finally {
        this.loading = false;
      }
    },

    extractTeamOptions() {
      const teams = new Set();
      this.players.forEach(player => {
        if (player.teamName) {
          teams.add(player.teamName);
        }
      });
      this.teamOptions = Array.from(teams).sort();
      console.log('提取的队伍选项:', this.teamOptions);
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
          (player.studentId && player.studentId.toString().includes(keyword)) ||
          (player.id && player.id.toString().includes(keyword))
        );
      }
      
      // 按队伍过滤
      if (this.selectedTeam) {
        filtered = filtered.filter(player => player.teamName === this.selectedTeam);
      }
      
      // 按赛事类型过滤
      if (this.selectedMatchType) {
        filtered = filtered.filter(player => player.matchType === this.selectedMatchType);
      }
      
      this.filteredPlayers = filtered;
      this.totalPlayers = filtered.length;
      this.currentPage = 1; // 重置到第一页
      
      console.log(`过滤后找到 ${this.filteredPlayers.length} 名球员`);
    },

    navigateToPlayerHistory(player) {
      console.log('点击球员:', player);
      
      const playerId = player.id || player.studentId;
      if (!playerId) {
        console.error('球员ID不存在:', player);
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
        console.log('成功跳转到球员详情页');
      }).catch(err => {
        console.error('路由跳转失败:', err);
        this.$message.error('页面跳转失败');
      });
    },

    async refreshPlayers() {
      console.log('手动刷新球员数据');
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
  height: 140px;
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
</style>
