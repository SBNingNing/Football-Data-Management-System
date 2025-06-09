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
            <span class="match-location"><i class="el-icon-location"></i> {{ match.location }}</span>
          </div>
        </div>
      </el-carousel-item>
    </el-carousel>
    <div v-else class="no-matches">
      <p>暂无近期比赛</p>
    </div>
  </el-card>
</template>

<script>
import { ElMessage } from 'element-plus';

export default {
  name: 'FeaturedMatches',
  props: {
    recentMatches: {
      type: Array,
      default: () => []
    }
  },
  methods: {
    getMatchTypeLabel(type) {
      const labels = {
        'championsCup': '冠军杯',
        'womensCup': '巾帼杯',
        'eightASide': '八人制',
        'champions-cup': '冠军杯',
        'womens-cup': '巾帼杯',
        'eight-a-side': '八人制'
      };
      return labels[type] || type || '';
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
          console.warn('Invalid date:', dateInput);
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
        console.error('Date formatting error:', error, dateInput);
        return '';
      }
    },
    viewMatchDetails(match) {
      if (match.id) {
        this.$router.push(`/matches/detail/${match.id}`);
      } else {
        ElMessage.error('未找到比赛ID');
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
  background: linear-gradient(135deg, #1e88e5, #0d47a1);
  color: white;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  cursor: pointer;
}

.featured-match-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.match-type-tag {
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 8px;
  border-radius: 4px;
}

.featured-match-teams {
  text-align: center;
  font-size: 22px;
  font-weight: bold;
  margin: 20px 0;
}

.vs {
  margin: 0 15px;
  color: #ffeb3b;
}

.featured-match-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.clearfix::after {
  content: "";
  display: table;
  clear: both;
}
</style>
