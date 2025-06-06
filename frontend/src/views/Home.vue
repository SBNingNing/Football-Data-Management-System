<template>
  <div class="home">
    <!-- 欢迎卡片 -->
    <el-card class="welcome-card">
      <template #header>
        <div class="clearfix">
          <span>足球管理系统欢迎您</span>
          <span @click="logout" style="float: right; margin-top: 8px; color: #409EFF; cursor: pointer;">
            退出
          </span>
        </div>
      </template>

      <!-- 数据统计卡片区域 -->
      <StatsCards :stats-data="statsData" />

      <!-- 赛事类型卡片区域 -->
      <MatchTypeCards />
    </el-card>

    <!-- 近期比赛轮播 -->
    <FeaturedMatches :recent-matches="recentMatches" />

    <!-- 排行数据 -->
    <RankingsSection 
      :rankings="rankings"
      :playoff-bracket="playoffBracket"
      :group-rankings="groupRankings"
      @competition-change="onCompetitionChange"
      @rankings-tab-change="onRankingsTabChange"
    />

    <!-- 比赛记录 -->
    <MatchRecords 
      :match-records="matchRecords"
      :match-records-total="matchRecordsTotal"
      @search="handleMatchSearch"
      @filter-change="handleMatchFilter"
      @page-change="handleMatchPageChange"
    />
  </div>
</template>

<script>
import axios from 'axios';
import { useUserStore } from '@/store';
import { ElMessage, ElMessageBox } from 'element-plus';
import StatsCards from '@/components/home/StatsCards.vue';
import MatchTypeCards from '@/components/home/MatchTypeCards.vue';
import FeaturedMatches from '@/components/home/FeaturedMatches.vue';
import RankingsSection from '@/components/home/RankingsSection.vue';
import MatchRecords from '@/components/home/MatchRecords.vue';

export default {
  name: 'Home',
  components: {
    StatsCards,
    MatchTypeCards,
    FeaturedMatches,
    RankingsSection,
    MatchRecords
  },
  data() {
    return {
      statsData: {
        totalMatches: 0,
        upcomingMatches: 0,
        completedMatches: 0
      },
      rankings: {
        championsCup: {
          topScorers: { players: [], teams: [] },
          cards: { players: [], teams: [] },
          points: []
        },
        womensCup: {
          topScorers: { players: [], teams: [] },
          cards: { players: [], teams: [] },
          points: []
        },
        eightASide: {
          topScorers: { players: [], teams: [] },
          cards: { players: [], teams: [] },
          points: []
        }
      },
      playoffBracket: {
        championsCup: [],
        womensCup: [],
        eightASide: []
      },
      groupRankings: {
        eightASide: {
          groups: []
        }
      },
      matchRecords: [],
      matchRecordsTotal: 0,
      recentMatches: [],
      isDataLoaded: false
    };
  },
  created() {
    console.log('Home component created, loading data...');
    this.loadAllData();
  },
  mounted() {
    console.log('Home component mounted');
    // 确保挂载后也执行数据加载
    if (!this.isDataLoaded) {
      this.$nextTick(() => {
        this.loadAllData();
      });
    }
  },
  activated() {
    console.log('Home component activated');
    // 当组件被激活时重新加载数据
    this.loadAllData();
  },
  beforeRouteEnter(to, from, next) {
    console.log('beforeRouteEnter - from:', from.path, 'to:', to.path);
    next(vm => {
      // 确保进入路由后加载数据
      vm.$nextTick(() => {
        vm.loadAllData();
      });
    });
  },
  watch: {
    '$route': {
      handler(to, from) {
        console.log('Route changed - from:', from?.path, 'to:', to.path);
        // 监听路由变化，确保返回主页时重新加载数据
        if (to.path === '/home' || to.name === 'Home') {
          this.$nextTick(() => {
            this.loadAllData();
          });
        }
      },
      immediate: true
    }
  },
  methods: {
    async loadAllData() {
      console.log('Loading all home data...');
      this.isDataLoaded = false;
      
      try {
        // 并行加载所有数据
        await Promise.allSettled([
          this.fetchStats(),
          this.fetchRankings(),
          this.fetchGroupRankings(),
          this.fetchPlayoffBracket(),
          this.fetchMatchRecords(),
          this.fetchRecentMatches()
        ]);
        
        this.isDataLoaded = true;
        console.log('All data loaded successfully');
      } catch (error) {
        console.error('Error loading data:', error);
        ElMessage.error('数据加载失败，请刷新页面重试');
      }
    },
    async fetchStats() {
      console.log('Fetching stats...');
      try {
        const response = await axios.get('/api/stats');
        console.log('Stats response:', response.data);
        
        if (response.data.status === 'success') {
          this.statsData = {
            totalMatches: response.data.data.totalMatches || 0,
            upcomingMatches: response.data.data.upcomingMatches || 0,
            completedMatches: response.data.data.completedMatches || 0
          };
        } else {
          console.error('Stats API error:', response.data.message);
          throw new Error(response.data.message || '获取统计数据失败');
        }
      } catch (error) {
        console.error('获取统计数据失败:', error);
        console.error('Error details:', error.response?.data);
        
        // 设置默认值
        this.statsData = {
          totalMatches: 0,
          upcomingMatches: 0,
          completedMatches: 0
        };
        
        // 只在第一次加载失败时显示错误信息
        if (!this.isDataLoaded) {
          ElMessage.warning('获取统计数据失败，请检查网络连接');
        }
      }
    },
    async fetchRankings() {
      try {
        const response = await axios.get('/api/rankings');
        if (response.data.status === 'success') {
          this.rankings = response.data.data;
        }
      } catch (error) {
        console.error('获取排行数据失败:', error);
        if (!this.isDataLoaded) {
          ElMessage.warning('获取排行数据失败');
        }
      }
    },
    async fetchGroupRankings() {
      try {
        const response = await axios.get('/api/group-rankings');
        if (response.data.status === 'success') {
          this.groupRankings = response.data.data;
        }
      } catch (error) {
        console.error('获取分组排名失败:', error);
      }
    },
    async fetchPlayoffBracket() {
      try {
        const response = await axios.get('/api/playoff-bracket');
        if (response.data.status === 'success') {
          this.playoffBracket = response.data.data;
        }
      } catch (error) {
        console.error('获取淘汰赛对阵失败:', error);
      }
    },
    async fetchMatchRecords(params = {}) {
      console.log('Fetching match records with params:', params);
      try {
        const requestParams = {
          type: params.type || '',
          keyword: params.keyword || '',
          page: params.page || 1,
          pageSize: params.pageSize || 10
        };

        const response = await axios.get('/api/matches/match-records', { params: requestParams });
        console.log('Match records response:', response.data);
        
        if (response.data.status === 'success') {
          this.matchRecords = (response.data.data.records || []).map(item => ({
            ...item,
            id: item.id || item.match_id || item.matchId
          }));
          this.matchRecordsTotal = response.data.data.total;
          console.log('Match records loaded:', this.matchRecords.length, 'total:', this.matchRecordsTotal);
        } else {
          console.warn('Match records API returned error:', response.data.message);
          this.matchRecords = [];
          this.matchRecordsTotal = 0;
        }
      } catch (error) {
        console.error('获取比赛记录失败:', error);
        console.error('Error details:', error.response?.data);
        this.matchRecords = [];
        this.matchRecordsTotal = 0;
        
        if (!this.isDataLoaded) {
          ElMessage.warning('获取比赛记录失败');
        }
      }
    },
    async fetchRecentMatches() {
      try {
        const response = await axios.get('/api/matches/match-records', {
          params: { page: 1, pageSize: 5 }
        });
        
        if (response.data.status === 'success') {
          this.recentMatches = response.data.data.records || [];
        }
      } catch (error) {
        console.error('获取近期比赛失败:', error);
      }
    },
    logout() {
      ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        const userStore = useUserStore();
        
        userStore.logout();
        
        localStorage.removeItem('userToken');
        localStorage.removeItem('userInfo');
        sessionStorage.clear();
        
        ElMessage.success('已退出登录');
        
        setTimeout(() => {
          window.location.href = '/login';
        }, 500);
      }).catch(() => {
        // 取消退出，不做任何操作
      });
    },
    onCompetitionChange(competition) {
      console.log('Competition changed to:', competition);
    },
    onRankingsTabChange(tab) {
      console.log('Rankings tab changed to:', tab);
    },
    handleMatchSearch(params) {
      this.fetchMatchRecords(params);
    },
    handleMatchFilter(params) {
      this.fetchMatchRecords(params);
    },
    handleMatchPageChange(params) {
      this.fetchMatchRecords(params);
    }
  }
};
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card {
  margin-bottom: 20px;
}

.clearfix::after {
  content: "";
  display: table;
  clear: both;
}
</style>