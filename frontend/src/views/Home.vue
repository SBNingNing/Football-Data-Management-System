<template>
  <div class="home">
    <!-- 
      后续游客登录状态判断逻辑：
      - 游客模式：仅显示欢迎卡片、统计卡片、比赛信息（只读）
      - 管理员模式：显示完整功能，包括管理入口
    -->
    <el-card class="welcome-card">
      <template #header>
        <div class="clearfix">
          <span>足球管理系统欢迎您</span>
          <!-- 游客界面权限控制入口：根据用户角色显示不同操作 -->
          <span @click="logout" class="logout-link">退出</span>
        </div>
      </template>
      <StatsCards :stats-data="statsData" />
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
        <FeaturedMatches :recent-matches="safeRecentMatches" />
      </template>
    </div>

    <!-- 
      后续权限扩展：排行榜区域
      - 游客：仅查看排行榜数据
      - 管理员：可能包含数据管理入口
    -->
    <RankingsSection 
      :rankings="rankings"
      :competitions="competitions"
      :seasons="seasons"
      :initial-season-id="selectedSeasonId"
      :playoff-bracket="playoffBracket"
      :group-rankings="groupRankings"
      @competition-change="onCompetitionChange"
      @season-change="handleSeasonChange"
      @rankings-tab-change="onRankingsTabChange"
    />

    <div class="block-section">
      <template v-if="_feedback?.errors.length">
        <ErrorBanner :error="_feedback.errors[0]" @retry="() => fetchMatchRecords({})" />
      </template>
      <template v-else>
        <!-- 
          比赛记录组件权限控制预留：
          - 游客仅显示查看功能
          - 管理员可能包含编辑/管理功能
        -->
        <MatchRecords 
          :match-records="matchRecords"
          :match-records-total="matchRecordsTotal"
          :selected-type="matchRecordsQuery ? matchRecordsQuery.type : ''"
          :selected-status="matchRecordsQuery ? matchRecordsQuery.status : ''"
          :competitions="competitions"
          :is-loading="_feedback?.pendings?.has('svc:match:records')"
          @search="handleMatchSearch"
          @filter-change="handleMatchFilter"
          @page-change="handleMatchPageChange"
          @reset="handleMatchReset"
        />
      </template>
    </div>

    <TeamSearch :competitions="competitions" :seasons="seasons" />
    <PlayerSearch :competitions="competitions" />
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

export default {
  name: 'Home',
  components: { StatsCards, MatchTypeCards, FeaturedMatches, RankingsSection, MatchRecords, TeamSearch, PlayerSearch, QuickNavigator, ErrorBanner, PanelSkeleton },
  setup() {
    const fb = useFeedback();
    const { text: statusTagText, tagType: statusTagType } = useStatusTag();
    const dashboard = useHomeDashboard({ feedback: fb });
    
    return {
      ...dashboard,
      _feedback: fb,
      statusTagText,
      statusTagType,
      // 暴露 dashboard 的 fetchMatchRecords 供 methods 调用
      dashboardFetchMatchRecords: dashboard.fetchMatchRecords
    };
  },
  computed: {
    // 确保recentMatches始终是数组类型
    safeRecentMatches() {
      return Array.isArray(this.recentMatches) ? this.recentMatches : []
    }
  },
  async mounted() {
    logger.info('Home mounted -> dashboard load')
    this._scroll = useScrollRestore({ key: 'home:records:initial' });
    await this.loadAllData();
    
    document.addEventListener('visibilitychange', this.handleVisibilityChange)
  },
  beforeUnmount() {
    document.removeEventListener('visibilitychange', this.handleVisibilityChange)
  },
  methods: {
    async fetchMatchRecords(params){ 
      // 直接调用 setup 中暴露的方法，无需手动同步数据，因为 setup 返回的是 ref
      await this.dashboardFetchMatchRecords(params); 
    },
    handleMatchSearch(p){ this.fetchMatchRecords(p) },
    handleMatchFilter(p){ this.fetchMatchRecords(p) },
    handleMatchPageChange(p){ this.fetchMatchRecords(p) },
    handleMatchReset(){
      // 传递空参数表示重置所有筛选条件
      this.fetchMatchRecords({ type:'', status:'', keyword:'', page:1, pageSize: this.matchRecordsQuery?.pageSize || 4 })
    },
    async refreshData(){ 
      // 直接调用 setup 中暴露的方法
      await this.loadAllData();
    },
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
      return this.statusTagType(status)
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