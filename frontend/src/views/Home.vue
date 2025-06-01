<template>
  <div class="home">
    <!-- 欢迎卡片 -->
    <el-card class="welcome-card">
      <div slot="header" class="clearfix">
        <span>足球管理系统欢迎您</span>
      </div>
      
      <!-- 数据统计卡片区域 -->
      <el-row :gutter="20" class="stats-section">
        <el-col :span="8">
          <el-card shadow="hover" class="stats-card">
            <div class="stats-card-inner">
              <i class="el-icon-data-line stats-icon"></i>
              <div class="stats-info">
                <div class="stats-number">{{ statsData.totalMatches }}</div>
                <div class="stats-label">总赛事数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card shadow="hover" class="stats-card">
            <div class="stats-card-inner">
              <i class="el-icon-timer stats-icon"></i>
              <div class="stats-info">
                <div class="stats-number">{{ statsData.upcomingMatches }}</div>
                <div class="stats-label">即将进行</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card shadow="hover" class="stats-card">
            <div class="stats-card-inner">
              <i class="el-icon-finished stats-icon"></i>
              <div class="stats-info">
                <div class="stats-number">{{ statsData.completedMatches }}</div>
                <div class="stats-label">已完成赛事</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 赛事类型卡片区域 -->
      <el-row :gutter="20" class="match-types">
        <el-col :span="8">
          <el-card shadow="hover" @click.native="$router.push('/matches/champions-cup')">
            <div class="match-type-card">
              <i class="el-icon-trophy"></i>
              <h3>冠军杯</h3>
              <p>查看冠军杯赛事信息</p>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card shadow="hover" @click.native="$router.push('/matches/womens-cup')">
            <div class="match-type-card">
              <i class="el-icon-female"></i>
              <h3>巾帼杯</h3>
              <p>查看巾帼杯赛事信息</p>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card shadow="hover" @click.native="$router.push('/matches/eight-a-side')">
            <div class="match-type-card">
              <i class="el-icon-basketball"></i>
              <h3>八人制比赛</h3>
              <p>查看八人制赛事信息</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    
    <!-- 热门比赛轮播 -->
    <el-card class="featured-matches-card">
      <div slot="header" class="clearfix">
        <span>热门比赛</span>
      </div>
      
      <el-carousel :interval="4000" type="card" height="200px">
        <el-carousel-item v-for="match in featuredMatches" :key="match.id">
          <div class="featured-match-item" @click="viewMatchDetails(match)">
            <div class="featured-match-header">
              <span class="match-type-tag">{{ match.type }}</span>
              <span class="match-date">{{ match.date }}</span>
            </div>
            <div class="featured-match-teams">
              <span class="team1">{{ match.team1 }}</span>
              <span class="vs">VS</span>
              <span class="team2">{{ match.team2 }}</span>
            </div>
            <div class="featured-match-footer">
              <span class="match-location"><i class="el-icon-location"></i> {{ match.location }}</span>
              <el-button size="mini" type="primary">查看详情</el-button>
            </div>
          </div>
        </el-carousel-item>
      </el-carousel>
    </el-card>
    
    <!-- 赛事公告 -->
    <el-card class="announcements-card">
      <div slot="header" class="clearfix">
        <span>赛事公告</span>
        <el-button style="float: right; padding: 3px 0" type="text">查看全部</el-button>
      </div>
      
      <el-timeline>
        <el-timeline-item
          v-for="(announcement, index) in announcements"
          :key="index"
          :timestamp="announcement.date"
          :type="announcement.type">
          <el-card>
            <h4>{{ announcement.title }}</h4>
            <p>{{ announcement.content }}</p>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </el-card>
    
    <!-- 近期比赛表格 -->
    <el-card class="recent-matches-card">
      <div slot="header" class="clearfix">
        <span>近期比赛</span>
      </div>
      <el-table :data="recentMatches" style="width: 100%">
        <el-table-column prop="name" label="比赛名称"></el-table-column>
        <el-table-column prop="type" label="类型"></el-table-column>
        <el-table-column prop="date" label="日期"></el-table-column>
        <el-table-column prop="location" label="地点"></el-table-column>
        <el-table-column label="对阵">
          <template slot-scope="scope">
            {{ scope.row.team1 }} vs {{ scope.row.team2 }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template slot-scope="scope">
            <el-button size="mini" type="primary" @click="viewMatchDetails(scope.row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Home',
  data() {
    return {
      recentMatches: [],
      featuredMatches: [],
      statsData: {
        totalMatches: 0,
        upcomingMatches: 0,
        completedMatches: 0
      },
      announcements: [
        {
          date: '2023-06-15',
          title: '冠军杯决赛将于本周六举行',
          content: '本赛季冠军杯决赛将于6月15日下午3点在主体育场举行，欢迎广大球迷到场观看。',
          type: 'success'
        },
        {
          date: '2023-06-10',
          title: '巾帼杯报名开始',
          content: '2023年巾帼杯足球赛报名已开始，请各参赛队伍于6月20日前完成报名手续。',
          type: 'warning'
        },
        {
          date: '2023-06-05',
          title: '赛事规程更新',
          content: '八人制比赛规程已更新，请各参赛队伍注意查看新规则。',
          type: 'info'
        }
      ]
    }
  },
  created() {
    this.fetchRecentMatches();
    this.fetchFeaturedMatches();
    this.fetchStats();
  },
  methods: {
    fetchRecentMatches() {
      axios.get('/api/matches')
        .then(response => {
          if (response.data.status === 'success') {
            this.recentMatches = response.data.data.slice(0, 5); // 只显示最近的5场比赛
          }
        })
        .catch(error => {
          console.error('获取比赛数据失败:', error);
          // 临时模拟数据
          this.recentMatches = [
            { id: 1, name: '冠军杯半决赛', type: '冠军杯', date: '2023-06-10 15:00:00', location: '主体育场', team1: '红牛队', team2: '蓝狮队' },
            { id: 2, name: '巾帼杯第三轮', type: '巾帼杯', date: '2023-06-12 14:00:00', location: '体育中心', team1: '凤凰队', team2: '飓风队' },
            { id: 3, name: '八人制联赛第5轮', type: '八人制', date: '2023-06-15 18:30:00', location: '西区球场', team1: '闪电队', team2: '雷霆队' }
          ];
        });
    },
    fetchFeaturedMatches() {
      // 实际项目中应从后端获取热门比赛数据
      // 这里使用模拟数据
      this.featuredMatches = [
        { id: 1, name: '冠军杯决赛', type: '冠军杯', date: '2023-06-15 15:00', location: '主体育场', team1: '红牛队', team2: '蓝狮队' },
        { id: 2, name: '巾帼杯半决赛', type: '巾帼杯', date: '2023-06-12 14:00', location: '体育中心', team1: '凤凰队', team2: '飓风队' },
        { id: 3, name: '八人制联赛焦点战', type: '八人制', date: '2023-06-18 18:30', location: '西区球场', team1: '闪电队', team2: '雷霆队' }
      ];
    },
    fetchStats() {
      // 实际项目中应从后端获取统计数据
      // 这里使用模拟数据
      this.statsData = {
        totalMatches: 24,
        upcomingMatches: 8,
        completedMatches: 16
      };
    },
    viewMatchDetails(match) {
      this.$router.push(`/matches/detail/${match.id}`);
    }
  }
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card,
.featured-matches-card,
.announcements-card,
.recent-matches-card {
  margin-bottom: 20px;
}

.stats-section {
  margin-bottom: 20px;
}

.stats-card {
  background-color: #f7f8fa;
  border: none;
  height: 100px;
}

.stats-card-inner {
  display: flex;
  align-items: center;
  height: 100%;
}

.stats-icon {
  font-size: 40px;
  color: #409EFF;
  margin-right: 15px;
}

.stats-info {
  display: flex;
  flex-direction: column;
}

.stats-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stats-label {
  font-size: 14px;
  color: #909399;
}

.match-types {
  margin-top: 20px;
}

.match-type-card {
  text-align: center;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.match-type-card:hover {
  transform: translateY(-5px);
}

.match-type-card i {
  font-size: 40px;
  margin-bottom: 10px;
  color: #409EFF;
}

.match-type-card h3 {
  margin-bottom: 10px;
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

.el-timeline-item {
  padding-bottom: 20px;
}

.el-timeline-item h4 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.el-timeline-item p {
  margin-top: 10px;
  color: #606266;
}

.el-divider {
  margin: 30px 0;
}

h2 {
  margin-bottom: 20px;
}
</style>
