<template>
  <el-card class="featured-matches-card">
    <template #header>
      <div class="clearfix">
        <span>近期比赛</span>
      </div>
    </template>

    <el-carousel :interval="4000" type="card" height="200px" v-if="recentMatches.length > 0">
      <el-carousel-item v-for="match in recentMatches" :key="match.id">
        <div class="featured-match-item" @click="viewMatchDetails(match)">
          <div class="featured-match-header">
            <span class="match-type-tag">{{ getMatchTypeLabel(match.type) }}</span>
            <span class="match-date">{{ formatDate(match.match_time) }}</span>
          </div>
          <div class="featured-match-teams">
            <span class="team1">{{ match.team1 }}</span>
            <span class="vs">VS</span>
            <span class="team2">{{ match.team2 }}</span>
          </div>
          <div class="featured-match-footer">
            <span class="match-location"><el-icon><LocationFilled /></el-icon> {{ match.location }}</span>
          </div>
        </div>
      </el-carousel-item>
    </el-carousel>
    <div v-else class="no-matches">
      <el-icon class="no-data-icon"><Calendar /></el-icon>
      <p>近期无比赛</p>
    </div>
  </el-card>
</template>

<script>
import logger from '@/utils/logger';
import { Calendar, LocationFilled } from '@element-plus/icons-vue'
import useCompetitions from '@/composables/admin/useCompetitions';

export default {
  name: 'FeaturedMatches',
  components: { Calendar, LocationFilled },
  setup() {
    const { getCompetitionLabel } = useCompetitions();
    return { getCompetitionLabel };
  },
  props: {
    recentMatches: {
      type: Array,
      default: () => [],
      validator: (value) => {
        // 确保传入的是数组
        return Array.isArray(value)
      }
    }
  },
  methods: {
    getMatchTypeLabel(type) {
      return this.getCompetitionLabel(type) || type || '';
    },
    formatDate(dateInput) {
      if (!dateInput) return '';
      
      try {
        let date;
        
        if (typeof dateInput === 'string') {
          const cleanDate = dateInput.replace(/[TZ]/g, ' ').replace(/\.\d{3}/, '').trim();
          date = new Date(cleanDate);
        } else {
          date = new Date(dateInput);
        }
        
        if (isNaN(date.getTime())) {
          logger.warn('Invalid date:', dateInput);
          return '';
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
  logger.error('Date formatting error:', error, dateInput);
        return '';
      }
    },
    viewMatchDetails(match) {
  logger.debug('查看比赛详情:', match);
      if (match.id) {
        // 使用路由名称进行跳转，确保与路由配置一致
        this.$router.push({
          name: 'match-detail', // 使用kebab-case命名的路由名称
          params: { matchId: match.id }
        }).catch(err => {
          logger.error('路由跳转失败:', err);
          // 如果路由名称不匹配，尝试使用path方式
          this.$router.push(`/match-detail/${match.id}`).catch(pathErr => {
            logger.error('路径跳转也失败:', pathErr);
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
.featured-matches-card {
  margin-bottom: 20px;
}

.featured-match-item {
  height: 100%;
  padding: 15px;
 background: #ffffff;
  color: #303133;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  cursor: pointer;
  border: 1px solid #e4e7ed;
  transition: all 0.3s;
}

.featured-match-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 20px 0 rgba(0, 0, 0, 0.1);
}

.featured-match-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.match-type-tag {
  background: #ecf5ff;
  color: #409eff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  border: 1px solid #d9ecff;
}

.featured-match-teams {
  text-align: center;
  font-size: 22px;
  font-weight: bold;
  margin: 20px 0;
  color: #303133;
}

.vs {
  margin: 0 15px;
  color: #909399;
  font-style: italic;
}

.featured-match-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #606266;
  font-size: 14px;
}

.no-matches {
  text-align: center;
  padding: 40px;
  color: #909399;
}

.no-matches p {
  margin: 0;
  font-size: 16px;
}

.no-data-icon {
  font-size: 48px;
  margin-bottom: 15px;
  color: #e0e0e0;
}

.clearfix::after {
  content: "";
  display: table;
  clear: both;
}
</style>
