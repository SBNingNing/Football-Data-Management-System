<template>
  <div class="schedule-input-wrapper">
  <el-form ref="scheduleForm" :model="scheduleForm" :rules="rules" label-width="120px" class="schedule-form">
      <el-row :gutter="24">
        <el-col :span="24">
          <el-form-item label="比赛名称" required>
            <el-input 
              v-model="scheduleForm.matchName" 
              placeholder="请输入比赛名称"
              size="large"
              clearable
              maxlength="100"
              show-word-limit
            >
              <template #prefix>
                <el-icon><Trophy /></el-icon>
              </template>
            </el-input>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="24">
        <el-col :md="12" :span="24">
          <el-form-item label="参赛球队1" prop="team1Id" required>
            <el-select 
              v-model="scheduleForm.team1Id" 
              placeholder="请选择球队1"
              size="large"
              style="width: 100%;"
              filterable
              clearable
              no-data-text="暂无可选球队"
            >
              <template #prefix>
                <el-icon><UserFilled /></el-icon>
              </template>
              <el-option 
                v-for="team in teams" 
                :key="team.id" 
                :label="team.teamName" 
                :value="team.id"
                :disabled="scheduleForm.team2Id === team.id"
              >
                <div class="team-option">
                  <span class="team-name">{{ team.teamName }}</span>
                  <span class="team-players">{{ team.players?.length || 0 }}名球员</span>
                </div>
              </el-option>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :md="12" :span="24">
          <el-form-item label="参赛球队2" prop="team2Id" required>
            <el-select 
              v-model="scheduleForm.team2Id" 
              placeholder="请选择球队2"
              size="large"
              style="width: 100%;"
              filterable
              clearable
              no-data-text="暂无可选球队"
            >
              <template #prefix>
                <el-icon><UserFilled /></el-icon>
              </template>
              <el-option 
                v-for="team in teams" 
                :key="team.id" 
                :label="team.teamName" 
                :value="team.id"
                :disabled="scheduleForm.team1Id === team.id"
              >
                <div class="team-option">
                  <span class="team-name">{{ team.teamName }}</span>
                  <span class="team-players">{{ team.players?.length || 0 }}名球员</span>
                </div>
              </el-option>
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="24">
        <el-col :md="12" :span="24">
          <el-form-item label="比赛日期" prop="date" required>
            <el-date-picker 
              v-model="scheduleForm.date" 
              type="datetime" 
              placeholder="选择日期时间"
              size="large"
              style="width: 100%;"
              format="YYYY-MM-DD HH:mm"
              value-format="YYYY-MM-DD HH:mm:ss"
              :disabled-date="disabledDate"
            >
              <template #prefix>
                <el-icon><Calendar /></el-icon>
              </template>
            </el-date-picker>
          </el-form-item>
        </el-col>
        <el-col :md="12" :span="24">
          <el-form-item label="比赛地点" prop="location" required>
            <el-input 
              v-model="scheduleForm.location" 
              placeholder="请输入比赛地点"
              size="large"
              clearable
              maxlength="50"
            >
              <template #prefix>
                <el-icon><MapLocation /></el-icon>
              </template>
            </el-input>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="24">
        <el-col :span="24">
          <el-form-item label="所属赛事实例" prop="tournamentId" required>
            <el-select
              v-model="scheduleForm.tournamentId"
              placeholder="请选择赛事实例"
              size="large"
              style="width:100%;"
              filterable
              clearable
              :disabled="tournamentsLoading"
              :no-data-text="tournamentsLoading ? '加载中...' : '暂无赛事实例'"
            >
              <el-option v-for="t in tournaments" :key="t.id" :label="t.name || ('Tournament#'+t.id)" :value="t.id" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 比赛预览卡片 -->
        <div v-if="isFormValid" class="match-preview-card">
          <div class="match-preview-header">
            <h4 class="match-preview-title">
              <el-icon><IconView /></el-icon>
              比赛预览
            </h4>
          </div>
          <div class="match-preview-content">
            <div class="match-info">
              <div class="match-preview-match-title">{{ scheduleForm.matchName }}</div>
              <div class="match-preview-teams">
                <div class="match-preview-team">
                  <el-avatar :size="40" class="match-preview-team-avatar">{{ team1Name?.charAt(0) }}</el-avatar>
                  <span class="match-preview-team-name">{{ team1Name }}</span>
                </div>
                <div class="match-preview-vs">VS</div>
                <div class="match-preview-team">
                  <el-avatar :size="40" class="match-preview-team-avatar">{{ team2Name?.charAt(0) }}</el-avatar>
                  <span class="match-preview-team-name">{{ team2Name }}</span>
                </div>
              </div>
              <div class="match-preview-details">
                <div class="match-preview-meta">
                  <el-icon><Calendar /></el-icon>
                  <span>{{ formatDate(scheduleForm.date) }}</span>
                </div>
                <div class="match-preview-meta">
                  <el-icon><MapLocation /></el-icon>
                  <span>{{ scheduleForm.location }}</span>
                </div>
              </div>
              <div class="match-preview-status">
                <el-tag type="success" size="small">待创建</el-tag>
              </div>
            </div>
          </div>
        </div>

      <el-form-item class="submit-form-item entity-submit-zone">
        <el-button 
          type="primary" 
          @click="handleSubmit"
          size="large"
          class="submit-btn btn-entity-submit"
          :disabled="!isFormValid || submitting"
          :loading="submitting"
        >
          <el-icon><Check /></el-icon>
          提交赛程信息
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { Trophy, UserFilled, Calendar, MapLocation, View as IconView, Check } from '@element-plus/icons-vue'
import { createMatch } from '@/domain/match/matchService'
import { fetchTournaments } from '@/domain/tournament/tournamentCrudService'

export default {
  name: 'ScheduleInput',
  components: {
    Trophy,
    UserFilled,
    Calendar,
    MapLocation,
  IconView,
    Check
  },
  props: {
    matchType: {
      type: String,
      default: ''
    },
    teams: {
      type: Array,
      default: () => []
    }
  },
  mounted(){
    this.loadTournaments()
  },
  // 声明组件可触发的事件，便于类型与 Lint 校验
  emits: ['submit'],
  data() {
    return {
      scheduleForm: {
        matchName: '',
        team1Id: null,
        team2Id: null,
        date: '',
        location: '',
        tournamentId: null
      },
      submitting: false,
      tournaments: [],
      tournamentsLoading: false,
      rules: {
        matchName: [{ required: true, message: '请输入比赛名称', trigger: 'blur' }],
        team1Id: [{ required: true, message: '请选择参赛球队1', trigger: 'change' }],
        team2Id: [{ required: true, message: '请选择参赛球队2', trigger: 'change' }],
        date: [{ required: true, message: '请选择比赛日期', trigger: 'change' }],
        location: [{ required: true, message: '请输入比赛地点', trigger: 'blur' }],
        tournamentId: [{ required: true, message: '请选择赛事实例', trigger: 'change' }]
      }
    }
  },
  computed: {
    isFormValid() {
      return this.scheduleForm.matchName.trim() && 
             this.scheduleForm.team1Id && 
             this.scheduleForm.team2Id && 
             this.scheduleForm.date && 
             this.scheduleForm.location.trim() &&
             this.scheduleForm.team1Id !== this.scheduleForm.team2Id &&
             this.scheduleForm.tournamentId
    },
    team1Name(){
      const t = this.teams.find(t=>t.id===this.scheduleForm.team1Id)
      return t?.teamName || ''
    },
    team2Name(){
      const t = this.teams.find(t=>t.id===this.scheduleForm.team2Id)
      return t?.teamName || ''
    }
  },
  methods: {
    async handleSubmit() {
      if (this.submitting) return;
      const formRef = this.$refs.scheduleForm
      if(formRef){
        try{ await formRef.validate() } catch{ return }
      } else if (!this.isFormValid) { this.$message.warning('请填写完整的赛程信息'); return }
      
      // 双方不可相同
      if(this.scheduleForm.team1Id === this.scheduleForm.team2Id){ this.$message.warning('两支参赛球队不能相同'); return }
      
      // 构造符合后端要求的数据格式
      let matchData = {
        matchName: this.scheduleForm.matchName,
        matchTime: this.scheduleForm.date, // 将date字段改为matchTime
        homeTeamId: this.scheduleForm.team1Id,
        awayTeamId: this.scheduleForm.team2Id,
        location: this.scheduleForm.location,
        tournamentId: this.scheduleForm.tournamentId || this.getTournamentIdByMatchType(this.matchType) // 添加tournamentId（优先选择器）
      };
      
      // 处理日期格式
      if (matchData.matchTime instanceof Date) {
        const pad = n => n < 10 ? '0' + n : n;
        const dt = new Date(matchData.matchTime.getTime());
        matchData.matchTime = `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())} ${pad(dt.getHours())}:${pad(dt.getMinutes())}:${pad(dt.getSeconds())}`;
      }
      
      try {
        this.submitting = true;
        const { ok, data, error } = await createMatch(matchData)
        if(!ok){
          this.$message.error(error?.message || '创建比赛失败')
          return
        }
        try {
          import('@/utils/httpClient').then(m=>{
            m.default.cache.invalidate('matches:records')
            m.default.cache.invalidate('stats:dashboard')
          })
  } catch { /* ignore cache invalidation errors */ }
        this.$message.success('比赛创建成功')
        this.$emit('submit', data || matchData)
        this.scheduleForm = { matchName: '', team1Id: null, team2Id: null, date: '', location: '', tournamentId: null };
  } catch{ 
        this.$message.error('创建比赛异常')
      } finally {
        this.submitting = false;
      }
    },
    
    // 根据比赛类型获取赛事ID
    getTournamentIdByMatchType(matchType) {
      // 这里需要根据实际业务逻辑返回对应的tournamentId
      // 暂时返回默认值1，后续可以根据需要从props或其他地方获取
      const tournamentMap = {
        'champions-cup': 1,
        'womens-cup': 2, 
        'eight-a-side': 3
      };
      return tournamentMap[matchType] || 1;
    },
    getMatchTypeLabel() {
      const labels = {
        'champions-cup': '冠军杯',
        'womens-cup': '巾帼杯',
        'eight-a-side': '八人制比赛'
      };
      return labels[this.matchType] || '';
    },
    async loadTournaments(){
      this.tournamentsLoading = true
      try{
        const { ok, data, error } = await fetchTournaments({ force:true })
        if(ok){ this.tournaments = Array.isArray(data)? data : [] }
        else { this.$message.info(error?.message || '无法加载赛事实例列表'); this.tournaments = [] }
      }catch{ this.tournaments = [] }
      finally{ this.tournamentsLoading = false }
    },
    disabledDate(time) {
      // 禁用过去的日期
      return time.getTime() < Date.now() - 8.64e7; // 24小时前
    },
    formatDate(date) {
      if (!date) return '';
      try {
        return new Date(date).toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          weekday: 'long'
        });
      } catch {
        return date;
      }
    }
  }
}
</script>

<style scoped>
/* 样式已迁移至 admin-management.css (.schedule-input-wrapper...) */
</style>