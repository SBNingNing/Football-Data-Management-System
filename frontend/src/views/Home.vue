<template>
  <div class="home">
    <el-card class="welcome-card">
      <template #header>
        <div class="clearfix">
          <span>足球管理系统欢迎您</span>
          <span @click="logout" class="logout-link">退出</span>
        </div>
      </template>
      <StatsCards :stats-data="statsData" />
      <MatchTypeCards />
    </el-card>

    <!-- 近期比赛区域：加载与错误反馈 -->
    <div class="block-section">
      <template v-if="_feedback?.pendings?.has('svc:recent-matches') && !_feedback?.errors.length">
        <PanelSkeleton :rows="3" />
      </template>
      <template v-else-if="_feedback?.errors.length">
        <ErrorBanner :error="_feedback.errors[0]" @retry="refreshData" />
      </template>
      <template v-else>
        <FeaturedMatches :recent-matches="recentMatches" />
      </template>
    </div>

    <RankingsSection 
      :rankings="rankings"
      :playoff-bracket="playoffBracket"
      :group-rankings="groupRankings"
      @competition-change="onCompetitionChange"
      @rankings-tab-change="onRankingsTabChange"
    />

    <div class="block-section">
      <template v-if="_feedback?.pendings?.has('svc:match:records') && !_feedback?.errors.length">
        <PanelSkeleton :rows="5" />
      </template>
      <template v-else-if="_feedback?.errors.length">
        <ErrorBanner :error="_feedback.errors[0]" @retry="() => fetchMatchRecords({})" />
      </template>
      <template v-else>
        <MatchRecords 
          :match-records="matchRecords"
          :match-records-total="matchRecordsTotal"
          @search="handleMatchSearch"
          @filter-change="handleMatchFilter"
          @page-change="handleMatchPageChange"
        />
      </template>
    </div>

    <TeamSearch />
    <PlayerSearch />
    <QuickNavigator />
  </div>
</template>

<script>
import logger from '@/utils/logger';
import { useScrollRestore } from '@/composables/scroll';
import { useFeedback } from '@/composables/ui';
import { useStatusTag } from '@/composables/meta';
import { useAuthStore } from '@/store/modules/auth';
import { useHomeDashboard } from '@/composables/domain/home/useHomeDashboard.js';
import { ElMessage, ElMessageBox } from 'element-plus';
import StatsCards from '@/components/home/StatsCards.vue';
import MatchTypeCards from '@/components/home/MatchTypeCards.vue';
import FeaturedMatches from '@/components/home/FeaturedMatches.vue';
import ErrorBanner from '@/components/common/ErrorBanner.vue';
import PanelSkeleton from '@/components/common/PanelSkeleton.vue';
import RankingsSection from '@/components/home/RankingsSection.vue';
import MatchRecords from '@/components/home/MatchRecords.vue';
import TeamSearch from '@/components/home/TeamSearch.vue';
import PlayerSearch from '@/components/home/PlayerSearch.vue';
import QuickNavigator from '@/components/home/QuickNavigator.vue';
// 数据加载已迁移至 useHomeDashboard 组合式

export default {
  name: 'Home',
  components: { StatsCards, MatchTypeCards, FeaturedMatches, RankingsSection, MatchRecords, TeamSearch, PlayerSearch, QuickNavigator, ErrorBanner, PanelSkeleton },
  data(){ return { matchRecords: [], matchRecordsTotal: 0 } },
  created() {
    const fb = useFeedback();
    const { text, tagType } = useStatusTag();
    this._feedback = fb; this._statusTagText = text; this._statusTagType = tagType;
    this._dash = useHomeDashboard({ feedback: fb });
    Object.assign(this, {
      statsData: this._dash.statsData,
      rankings: this._dash.rankings,
      playoffBracket: this._dash.playoffBracket,
      groupRankings: this._dash.groupRankings,
      recentMatches: this._dash.recentMatches,
      retryCount: this._dash.retryCount,
      isPageRefresh: this._dash.isPageRefresh
    });
  },
  async mounted() {
    logger.info('Home mounted -> dashboard load')
    this._scroll = useScrollRestore({ key: 'home:records:initial' });
    await this._dash.loadAllData();
    document.addEventListener('visibilitychange', this._dash.handleVisibilityChange)
  },
  beforeUnmount() {
    document.removeEventListener('visibilitychange', this._dash.handleVisibilityChange)
  },
  methods: {
    fetchMatchRecords(params){ this._dash.fetchMatchRecords(params); this.matchRecords = this._dash.matchRecords.value; this.matchRecordsTotal = this._dash.matchRecordsTotal.value; },
    handleMatchSearch(p){ this.fetchMatchRecords(p) },
    handleMatchFilter(p){ this.fetchMatchRecords(p) },
    handleMatchPageChange(p){ this.fetchMatchRecords(p) },
    refreshData(){ this._dash.refreshData() },
    logout() {
      ElMessageBox.confirm('确定要退出登录吗？', '提示', { confirmButtonText:'确定', cancelButtonText:'取消', type:'warning' })
        .then(() => {
          const auth = useAuthStore(); auth.logout();
          localStorage.removeItem('userToken'); localStorage.removeItem('userInfo'); sessionStorage.clear();
          ElMessage.success('已退出登录');
          setTimeout(() => this.$router.push('/login'), 400)
        }).catch(()=>{})
    },
    onCompetitionChange(c){ logger.debug('Competition change', c) },
    onRankingsTabChange(t){ logger.debug('Rankings tab change', t) },
    getStatusType(status){
      return this._statusTagType(status)
    }
  }
}
</script>

<style scoped>
.home { max-width:1200px; margin:0 auto; position:relative; }
.welcome-card { margin-bottom:20px; }
.clearfix::after { content:""; display:table; clear:both; }
.logout-link { float:right; margin-top:8px; color:#409EFF; cursor:pointer; }
</style>