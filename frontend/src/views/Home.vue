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

    <!-- 球员搜索模块 -->
    <PlayerSearch />
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
import PlayerSearch from '@/components/home/PlayerSearch.vue';

export default {
  name: 'Home',
  components: {
    StatsCards,
    MatchTypeCards,
    FeaturedMatches,
    RankingsSection,
    MatchRecords,
    PlayerSearch
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
      loading: false,
      retryCount: 0,
      maxRetries: 3,
      isPageRefresh: false
    };
  },
  created() {
    // 检测是否是页面刷新
    this.isPageRefresh = !window.performance || window.performance.navigation.type === 1;
    console.log('Home component created, is page refresh:', this.isPageRefresh);
  },
  async mounted() {
    console.log('Home component mounted, loading data...');
    // 无论是否刷新都加载数据
    await this.loadAllData();
    
    // 监听页面可见性变化（从其他标签页返回时重新加载）
    document.addEventListener('visibilitychange', this.handleVisibilityChange);
    
    // 监听窗口焦点事件
    window.addEventListener('focus', this.handleWindowFocus);
  },
  beforeUnmount() {
    // 清理事件监听器
    document.removeEventListener('visibilitychange', this.handleVisibilityChange);
    window.removeEventListener('focus', this.handleWindowFocus);
  },
  methods: {
    handleVisibilityChange() {
      if (!document.hidden) {
        console.log('Page became visible, refreshing data...');
        this.loadAllData();
      }
    },
    
    handleWindowFocus() {
      console.log('Window focused, refreshing data...');
      this.loadAllData();
    },

    async loadAllData() {
      if (this.loading) return;
      
      console.log('Loading all home data...', { isPageRefresh: this.isPageRefresh });
      this.loading = true;
      
      try {
        // 如果是页面刷新，增加延迟确保DOM完全加载
        if (this.isPageRefresh) {
          await new Promise(resolve => setTimeout(resolve, 500));
        }
        
        // 串行加载关键数据，确保顺序
        await this.fetchStats();
        
        // 并行加载其他数据
        const promises = [
          this.fetchRankings(),
          this.fetchGroupRankings(),
          this.fetchPlayoffBracket(),
          this.fetchMatchRecords(),
          this.fetchRecentMatches()
        ];
        
        const results = await Promise.allSettled(promises);
        
        // 检查是否有失败的请求
        const failedRequests = results.filter(result => result.status === 'rejected');
        if (failedRequests.length > 0) {
          console.warn('Some requests failed:', failedRequests);
        }
        
        console.log('All data loaded successfully');
        this.retryCount = 0; // 重置重试计数
        this.isPageRefresh = false; // 重置刷新标志
      } catch (error) {
        console.error('Error loading data:', error);
        this.handleLoadError();
      } finally {
        this.loading = false;
      }
    },
    
    handleLoadError() {
      if (this.retryCount < this.maxRetries) {
        this.retryCount++;
        console.log(`Retrying data load (${this.retryCount}/${this.maxRetries})...`);
        setTimeout(() => {
          this.loadAllData();
        }, 2000 * this.retryCount); // 递增延迟重试
      } else {
        ElMessage.error('数据加载失败，请刷新页面重试');
        this.retryCount = 0; // 重置重试计数以便下次重新开始
      }
    },

    async fetchStats() {
      console.log('Fetching stats...');
      try {
        const response = await axios.get('/api/stats', {
          timeout: 15000, // 增加超时时间
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
          }
        });
        console.log('Stats response:', response.data);
        
        if (response.data && response.data.status === 'success') {
          this.statsData = {
            totalMatches: response.data.data?.totalMatches || 0,
            upcomingMatches: response.data.data?.upcomingMatches || 0,
            completedMatches: response.data.data?.completedMatches || 0
          };
          console.log('Stats data updated:', this.statsData);
        } else {
          throw new Error(response.data?.message || '获取统计数据失败');
        }
      } catch (error) {
        console.error('获取统计数据失败:', error);
        this.statsData = {
          totalMatches: 0,
          upcomingMatches: 0,
          completedMatches: 0
        };
        throw error;
      }
    },

    async fetchGroupRankings() {
      try {
        const response = await axios.get('/api/group-rankings', {
          timeout: 15000,
          headers: {
            'Cache-Control': 'no-cache'
          }
        });
        if (response.data?.status === 'success') {
          this.groupRankings = response.data.data || this.groupRankings;
        }
      } catch (error) {
        console.error('获取分组排名失败:', error);
        // 不再抛出错误，而是默默处理失败情况
        return Promise.resolve();
      }
    },

    async fetchPlayoffBracket() {
      try {
        const response = await axios.get('/api/playoff-bracket', {
          timeout: 15000,
          headers: {
            'Cache-Control': 'no-cache'
          }
        });
        if (response.data?.status === 'success') {
          this.playoffBracket = response.data.data || this.playoffBracket;
        }
      } catch (error) {
        console.error('获取淘汰赛对阵失败:', error);
        // 不再抛出错误，而是默默处理失败情况
        return Promise.resolve();
      }
    },

    async fetchRankings() {
      console.log('开始获取排行数据...');
      try {
        const response = await axios.get('/api/rankings', {
          timeout: 15000,
          headers: {
            'Cache-Control': 'no-cache'
          }
        });
        
        console.log('Rankings API 原始响应:', response.data);
        
        if (response.data?.status === 'success') {
          const apiData = response.data.data;
          console.log('Rankings API 数据部分:', apiData);
          
          // 确保数据结构完整
          const defaultRankingData = {
            topScorers: { players: [], teams: [] },
            cards: { players: [], teams: [] },
            points: []
          };
          
          // 处理每个赛事类型的数据
          this.rankings = {
            championsCup: this.processRankingData(apiData?.championsCup, defaultRankingData, '冠军杯'),
            womensCup: this.processRankingData(apiData?.womensCup, defaultRankingData, '女子杯'),
            eightASide: this.processRankingData(apiData?.eightASide, defaultRankingData, '八人制')
          };
          
          console.log('处理后的rankings数据:', this.rankings);
        } else {
          console.warn('Rankings API 返回状态异常:', response.data);
          this.setDefaultRankings();
        }
      } catch (error) {
        console.error('获取排行数据失败:', error);
        this.setDefaultRankings();
        return Promise.resolve();
      }
    },

    // 新增：处理单个赛事类型的排行数据
    processRankingData(competitionData, defaultData, competitionName) {
      console.log(`处理${competitionName}数据:`, competitionData);
      
      if (!competitionData) {
        console.log(`${competitionName}数据为空，使用默认数据`);
        return { ...defaultData };
      }
      
      const processed = {
        topScorers: {
          players: this.processPlayersData(competitionData.topScorers?.players, '射手'),
          teams: competitionData.topScorers?.teams || []
        },
        cards: {
          players: this.processPlayersData(competitionData.cards?.players, '红黄牌'),
          teams: competitionData.cards?.teams || []
        },
        points: competitionData.points || []
      };
      
      console.log(`${competitionName}处理后数据:`, processed);
      return processed;
    },

    // 新增：处理球员数据
    processPlayersData(playersData, type) {
      if (!Array.isArray(playersData)) {
        console.log(`${type}球员数据不是数组:`, playersData);
        return [];
      }
      
      const processed = playersData.map(player => ({
        id: player.id || player.player_id || `${type}_${Math.random()}`,
        name: player.name || player.player_name || '未知球员',
        teamName: player.teamName || player.team_name || '未知队伍',
        goals: player.goals || 0,
        yellowCards: player.yellowCards || player.yellow_cards || 0,
        redCards: player.redCards || player.red_cards || 0,
        totalCards: player.totalCards || player.total_cards || 0,
        ...player
      }));
      
      console.log(`处理后的${type}球员数据:`, processed);
      return processed;
    },

    // 新增：设置默认排行数据
    setDefaultRankings() {
      const defaultRankingData = {
        topScorers: { players: [], teams: [] },
        cards: { players: [], teams: [] },
        points: []
      };
      
      this.rankings = {
        championsCup: { ...defaultRankingData },
        womensCup: { ...defaultRankingData },
        eightASide: { ...defaultRankingData }
      };
      
      console.log('设置默认rankings数据');
    },

    async fetchMatchRecords(params = {}) {
      console.log('Fetching match records with params:', params);
      try {
        const requestParams = {
          type: params.type || '',
          status: params.status || '',
          keyword: params.keyword || '',
          page: params.page || 1,
          pageSize: params.pageSize || 10
        };

        console.log('Request params for match records:', requestParams);

        const response = await axios.get('/api/matches/match-records', { 
          params: requestParams,
          timeout: 15000,
          headers: {
            'Cache-Control': 'no-cache'
          }
        });
        console.log('Match records response:', response.data);
        
        if (response.data?.status === 'success') {
          const records = response.data.data?.records || [];
          console.log('Raw match records from API:', records);
          
          this.matchRecords = records.map(item => {
            const processedItem = {
              ...item,
              id: item.id || item.match_id || item.matchId || Math.random().toString(),
              // 确保比分和状态字段存在
              score: item.score || `${item.home_score || 0} : ${item.away_score || 0}`,
              status: item.status || '待进行',
              status_type: this.getStatusType(item.status),
              // 确保所有必要字段都存在
              name: item.name || item.match_name || `${item.team1 || '队伍1'} vs ${item.team2 || '队伍2'}`,
              team1: item.team1 || item.home_team || '队伍1',
              team2: item.team2 || item.away_team || '队伍2',
              date: item.date || item.match_time || '',
              location: item.location || '待定',
              type: item.type || 'championsCup'
            };
            console.log('Processed match item:', processedItem);
            return processedItem;
          });
          
          this.matchRecordsTotal = response.data.data?.total || this.matchRecords.length;
          console.log('Final match records:', this.matchRecords);
          console.log('Total records:', this.matchRecordsTotal);
        } else {
          console.warn('Match records API returned error:', response.data?.message);
          this.matchRecords = [];
          this.matchRecordsTotal = 0;
        }
      } catch (error) {
        console.error('获取比赛记录失败:', error);
        this.matchRecords = [];
        this.matchRecordsTotal = 0;
        return Promise.resolve();
      }
    },

    // 新增：根据状态获取标签类型
    getStatusType(status) {
      const statusMap = {
        '待进行': 'info',
        '进行中': 'warning', 
        '已完赛': 'success',
        'pending': 'info',
        'ongoing': 'warning',
        'completed': 'success'
      };
      return statusMap[status] || 'info';
    },

    async fetchRecentMatches() {
      try {
        const response = await axios.get('/api/matches/match-records', {
          params: { page: 1, pageSize: 5 },
          timeout: 15000,
          headers: {
            'Cache-Control': 'no-cache'
          }
        });
        
        if (response.data?.status === 'success') {
          this.recentMatches = response.data.data?.records || [];
        }
      } catch (error) {
        console.error('获取近期比赛失败:', error);
        // 不再抛出错误，而是默默处理失败情况
        return Promise.resolve();
      }
    },

    // 手动刷新数据的方法
    async refreshData() {
      console.log('Manual refresh triggered');
      this.retryCount = 0; // 重置重试计数
      await this.loadAllData();
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
          this.$router.push('/login');
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
      console.log('Home: handleMatchSearch called with:', params);
      this.fetchMatchRecords(params);
    },

    handleMatchFilter(params) {
      console.log('Home: handleMatchFilter called with:', params);
      this.fetchMatchRecords(params);
    },

    handleMatchPageChange(params) {
      console.log('Home: handleMatchPageChange called with:', params);
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