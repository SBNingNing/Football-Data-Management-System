<template>
  <el-card class="match-records-card">
    <template #header>
      <div class="card-header">
        <span>比赛记录</span>
        <div class="search-stats">
          共找到 {{ matchRecordsTotal }} 场比赛
        </div>
      </div>
    </template>

    <!-- 搜索区域 -->
    <div class="search-section">
      <el-row :gutter="15">
        <el-col :span="6">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索比赛名称、球队或地点"
            @input="handleSearch"
            clearable
            class="search-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select
            v-model="selectedType"
            placeholder="选择比赛类型"
            @change="handleFilterChange"
            clearable
            class="type-select"
          >
            <el-option label="冠军杯" value="championsCup" />
            <el-option label="巾帼杯" value="womensCup" />
            <el-option label="八人制" value="eightASide" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select
            v-model="selectedStatus"
            placeholder="选择比赛状态"
            @change="handleStatusFilter"
            clearable
            class="status-select"
          >
            <el-option label="待进行" value="pending" />
            <el-option label="进行中" value="ongoing" />
            <el-option label="已完赛" value="completed" />
          </el-select>
        </el-col>
        <el-col :span="3">
          <el-button 
            type="primary" 
            @click="refreshMatches"
            :loading="loading"
            class="refresh-button"
          >
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 比赛列表 -->
    <div class="matches-section" v-loading="loading" element-loading-text="正在加载比赛数据...">
      <div v-if="matchRecords.length === 0 && !loading" class="no-matches">
        <el-icon class="no-data-icon"><Calendar /></el-icon>
        <p>{{ searchKeyword || selectedType || selectedStatus ? '未找到符合条件的比赛' : '暂无比赛数据' }}</p>
      </div>
      
      <el-row :gutter="20" v-else>
        <el-col 
          :span="12" 
          v-for="match in displayMatchRecords" 
          :key="match.id"
          class="match-col"
        >
          <el-card 
            shadow="hover" 
            class="match-card"
            @click="viewMatchDetails(match)"
          >
            <div class="match-header">
              <div class="match-type-tag">
                <el-tag :type="getMatchTypeColor(match.type)" size="small">
                  {{ getMatchTypeLabel(match.type) }}
                </el-tag>
              </div>
              <div class="match-status">
                <el-tag :type="match.status_type" size="small">
                  {{ match.status }}
                </el-tag>
              </div>
            </div>
            
            <div class="match-title">
              {{ match.name || '比赛' }}
            </div>
            
            <div class="match-teams">
              <div class="team team-home">
                <span class="team-name">{{ match.team1 }}</span>
              </div>
              <div class="match-vs">
                <div class="vs-text">VS</div>
                <div class="match-score" :class="getScoreClass(match.status)">
                  {{ match.score }}
                </div>
              </div>
              <div class="team team-away">
                <span class="team-name">{{ match.team2 }}</span>
              </div>
            </div>
            
            <div class="match-info">
              <div class="info-item">
                <el-icon><Clock /></el-icon>
                <span>{{ formatDate(match.date) }}</span>
              </div>
              <div class="info-item">
                <el-icon><LocationFilled /></el-icon>
                <span>{{ match.location || '待定' }}</span>
              </div>
            </div>
            
            <div class="match-card-overlay">
              <el-icon><View /></el-icon>
              <span>查看详情</span>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper" v-if="matchRecordsTotal > pageSize">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[4, 8, 12, 16]"
        :total="matchRecordsTotal"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </el-card>
</template>

<script>
import { 
  Search, 
  Refresh, 
  Calendar, 
  Clock, 
  LocationFilled, 
  View 
} from '@element-plus/icons-vue';

export default {
  name: 'MatchRecords',
  components: {
    Search,
    Refresh,
    Calendar,
    Clock,
    LocationFilled,
    View
  },
  props: {
    matchRecords: {
      type: Array,
      default: () => []
    },
    matchRecordsTotal: {
      type: Number,
      default: 0
    }
  },
  data() {
    return {
      selectedType: '',
      selectedStatus: '',
      searchKeyword: '',
      currentPage: 1,
      pageSize: 4,
      searchTimer: null,
      loading: false
    };
  },
  computed: {
    // 计算属性：确保只显示当前页应该显示的比赛数量
    displayMatchRecords() {
      // 如果matchRecords数组长度超过pageSize，只取前pageSize个
      if (this.matchRecords.length > this.pageSize) {
        return this.matchRecords.slice(0, this.pageSize);
      }
      return this.matchRecords;
    }
  },
  watch: {
    // 监听props变化，确保数据更新
    matchRecords: {
      handler(newVal) {
        console.log('MatchRecords props updated:', newVal);
      },
      immediate: true
    },
    matchRecordsTotal: {
      handler(newVal) {
        console.log('MatchRecordsTotal props updated:', newVal);
      },
      immediate: true
    }
  },
  mounted() {
    // 组件挂载后立即发送请求，确保使用正确的分页参数
    this.$nextTick(() => {
      this.emitDataRequest('filter-change');
    });
  },
  methods: {
    // 统一的数据获取方法
    emitDataRequest(eventType = 'filter-change') {
      const params = {
        type: this.selectedType,
        status: this.selectedStatus,
        keyword: this.searchKeyword,
        page: this.currentPage,
        pageSize: this.pageSize
      };
      
      console.log(`${eventType} triggered:`, params);
      this.$emit(eventType, params);
    },

    handleFilterChange() {
      this.currentPage = 1;
      this.emitDataRequest('filter-change');
    },

    handleStatusFilter() {
      this.currentPage = 1;
      this.emitDataRequest('filter-change');
    },

    handleSearch() {
      if (this.searchTimer) {
        clearTimeout(this.searchTimer);
      }
      this.searchTimer = setTimeout(() => {
        this.currentPage = 1;
        this.emitDataRequest('search');
      }, 300);
    },

    handleSizeChange(val) {
      this.pageSize = val;
      this.currentPage = 1;
      this.emitDataRequest('page-change');
    },

    handleCurrentChange(val) {
      this.currentPage = val;
      this.emitDataRequest('page-change');
    },

    refreshMatches() {
      console.log('手动刷新比赛数据');
      this.loading = true;
      this.emitDataRequest('filter-change');
      setTimeout(() => {
        this.loading = false;
      }, 1000);
    },

    // 修正比赛类型映射，确保与后端一致
    getMatchTypeLabel(type) {
      const labels = {
        'championsCup': '冠军杯',
        'womensCup': '巾帼杯', 
        'eightASide': '八人制',
        'champions-cup': '冠军杯',
        'womens-cup': '巾帼杯',
        'eight-a-side': '八人制',
        '冠军杯': '冠军杯',
        '巾帼杯': '巾帼杯',
        '八人制': '八人制'
      };
      return labels[type] || type || '未知';
    },

    getMatchTypeColor(type) {
      const colors = {
        'championsCup': 'warning',
        'womensCup': 'danger',
        'eightASide': 'success',
        'champions-cup': 'warning',
        'womens-cup': 'danger', 
        'eight-a-side': 'success',
        '冠军杯': 'warning',
        '巾帼杯': 'danger',
        '八人制': 'success'
      };
      return colors[type] || 'info';
    },

    getScoreClass(status) {
      return status === '已完赛' ? 'final-score' : 'pending-score';
    },

    formatDate(dateInput) {
      if (!dateInput) return '时间待定';
      
      try {
        let date;
        
        if (typeof dateInput === 'string') {
          const cleanDate = dateInput.replace(/[TZ]/g, ' ').replace(/\.\d{3}/, '').trim();
          date = new Date(cleanDate);
        } else {
          date = new Date(dateInput);
        }
        
        if (isNaN(date.getTime())) {
          return '时间待定';
        }
        
        return date.toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          timeZone: 'Asia/Shanghai'
        });
      } catch (error) {
        console.error('Date formatting error:', error, dateInput);
        return '时间待定';
      }
    },

    viewMatchDetails(match) {
      console.log('查看比赛详情:', match);
      if (match.id) {
        // 使用路由名称进行跳转，确保与路由配置一致
        this.$router.push({
          name: 'match-detail', // 使用kebab-case命名的路由名称
          params: { matchId: match.id }
        }).catch(err => {
          console.error('路由跳转失败:', err);
          // 如果路由名称不匹配，尝试使用path方式
          this.$router.push(`/match-detail/${match.id}`).catch(pathErr => {
            console.error('路径跳转也失败:', pathErr);
            this.$message.error('页面跳转失败，请检查路由配置');
          });
        });
      } else {
        this.$message.error('未找到比赛ID');
      }
    }
  }
};
</script>

<style scoped>
.match-records-card {
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
.type-select,
.status-select {
  width: 100%;
}

.refresh-button {
  width: 100%;
}

.matches-section {
  min-height: 400px;
}

.no-matches {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.no-data-icon {
  font-size: 48px;
  margin-bottom: 15px;
  color: #e0e0e0;
}

.match-col {
  margin-bottom: 20px;
}

.match-card {
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  height: 280px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 20px;
}

.match-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.match-card:hover .match-card-overlay {
  opacity: 1;
}

.match-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-shrink: 0;
}

.match-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 15px;
  text-align: center;
  line-height: 1.4;
  word-wrap: break-word;
  overflow-wrap: break-word;
  flex-shrink: 0;
  max-height: 44px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
}

.match-teams {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
  padding: 20px 0;
  flex: 1;
  min-height: 100px;
}

.team {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  max-width: 35%;
}

.team-home {
  justify-content: flex-start;
  text-align: left;
}

.team-away {
  justify-content: flex-end;
  text-align: right;
}

.team-name {
  font-size: 18px;
  font-weight: 600;
  color: #606266;
  line-height: 1.3;
  word-wrap: break-word;
  overflow-wrap: break-word;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  width: 100%;
  width: 100%;
}

.team-home .team-name {
  text-align: left;
}

.team-away .team-name {
  text-align: right;
}

.match-vs {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex-shrink: 0;
  margin: 0 15px;
  min-width: 80px;
  height: 100%;
}

.vs-text {
  font-size: 14px;
  color: #909399;
  font-weight: bold;
}

.match-score {
  font-size: 16px;
  font-weight: bold;
  padding: 6px 10px;
  border-radius: 6px;
  min-width: 60px;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 80px;
}

.final-score {
  background-color: #e8f5e8;
  color: #67c23a;
}

.pending-score {
  background-color: #f4f4f5;
  color: #909399;
}

.match-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-shrink: 0;
  text-align: center;
}

.info-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 13px;
  color: #606266;
  line-height: 1.4;
  min-height: 20px;
}

.info-item .el-icon {
  font-size: 14px;
  color: #909399;
  flex-shrink: 0;
}

.info-item span {
  word-wrap: break-word;
  overflow-wrap: break-word;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
}

.match-card-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(64, 158, 255, 0.75);
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  opacity: 0;
  transition: opacity 0.3s ease;
  font-weight: 500;
  backdrop-filter: blur(2px);
}

.match-card-overlay .el-icon {
  font-size: 28px;
  margin-bottom: 4px;
}

.match-card-overlay span {
  font-size: 16px;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.pagination-wrapper {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .match-card {
    height: 260px;
  }
  
  .team-name {
    font-size: 16px;
  }
  
  .match-score {
    font-size: 15px;
    padding: 5px 8px;
  }
}

@media (max-width: 768px) {
  .match-card {
    height: 240px;
    padding: 15px;
  }
  
  .match-teams {
    padding: 15px 0;
    min-height: 80px;
  }
  
  .team {
    max-width: 30%;
  }
  
  .team-name {
    font-size: 14px;
    max-height: 36px;
  }
  
  .match-score {
    font-size: 14px;
    padding: 4px 6px;
    min-width: 50px;
    max-width: 60px;
  }
  
  .vs-text {
    font-size: 12px;
  }
  
  .info-item {
    font-size: 12px;
    gap: 4px;
  }
  
  .info-item span {
    max-width: 150px;
  }
  
  .match-title {
    font-size: 14px;
    margin-bottom: 12px;
    max-height: 40px;
  }
  
  .match-vs {
    margin: 0 10px;
    min-width: 60px;
  }
}

@media (max-width: 480px) {
  .match-card {
    height: 220px;
    padding: 12px;
  }
  
  .team-name {
    font-size: 12px;
    max-height: 32px;
  }
  
  .match-score {
    font-size: 13px;
    max-width: 50px;
  }
  
  .info-item span {
    max-width: 120px;
  }
  
  .match-title {
    font-size: 13px;
    max-height: 36px;
  }
}
</style>
