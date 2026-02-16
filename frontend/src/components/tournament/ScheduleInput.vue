<template>
  <div class="schedule-input-wrapper">
  <el-form ref="scheduleForm" :model="scheduleForm" :rules="rules" label-width="120px" class="schedule-form">
      <el-row :gutter="24">
        <el-col :span="24">
          <el-form-item label="比赛名称" prop="match_name" required>
            <el-input 
              v-model="scheduleForm.match_name" 
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
          <el-form-item label="参赛球队1" prop="team1_id" required>
            <el-select 
              v-model="scheduleForm.team1_id" 
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
                :label="team.team_name" 
                :value="team.id"
                :disabled="scheduleForm.team2_id === team.id"
              >
                <div class="team-option">
                  <span class="team-name">{{ team.team_name }}</span>
                  <span class="team-players">{{ team.players?.length || 0 }}名球员</span>
                </div>
              </el-option>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :md="12" :span="24">
          <el-form-item label="参赛球队2" prop="team2_id" required>
            <el-select 
              v-model="scheduleForm.team2_id" 
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
                :label="team.team_name" 
                :value="team.id"
                :disabled="scheduleForm.team1_id === team.id"
              >
                <div class="team-option">
                  <span class="team-name">{{ team.team_name }}</span>
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
              <div class="match-preview-match-title">{{ scheduleForm.match_name }}</div>
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
import { createMatch } from '@/api/matches'
import { fetchTournaments } from '@/api/tournaments'

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
      type: [String, Number],
      default: ''
    },
    tournamentId: {
      type: [String, Number],
      default: ''
    },
    teams: {
      type: Array,
      default: () => []
    }
  },
  // 声明组件可触发的事件，便于类型与 Lint 校验
  emits: ['submit'],
  data() {
    return {
      scheduleForm: {
        match_name: '',
        team1_id: null,
        team2_id: null,
        date: '',
        location: '',
        tournament_id: null
      },
      submitting: false,
      tournaments: [],
      tournamentsLoading: false,
      rules: {
        match_name: [{ required: true, message: '请输入比赛名称', trigger: 'blur' }],
        team1_id: [{ required: true, message: '请选择参赛球队1', trigger: 'change' }],
        team2_id: [{ required: true, message: '请选择参赛球队2', trigger: 'change' }],
        date: [{ required: true, message: '请选择比赛日期', trigger: 'change' }],
        location: [{ required: true, message: '请输入比赛地点', trigger: 'blur' }],
      }
    }
  },
  computed: {
    isFormValid() {
      return this.scheduleForm.match_name.trim() && 
             this.scheduleForm.team1_id && 
             this.scheduleForm.team2_id && 
             this.scheduleForm.date && 
             this.scheduleForm.location.trim() &&
             this.scheduleForm.team1_id !== this.scheduleForm.team2_id
    },
    team1Name(){
      const t = this.teams.find(t=>t.id===this.scheduleForm.team1_id)
      return t?.team_name || ''
    },
    team2Name(){
      const t = this.teams.find(t=>t.id===this.scheduleForm.team2_id)
      return t?.team_name || ''
    }
  },
  mounted(){
    this.loadTournaments()
  },
  methods: {
    async handleSubmit() {
      if (this.submitting) return;
      const formRef = this.$refs.scheduleForm
      if(formRef){
        try{ await formRef.validate() } catch{ return }
      } else if (!this.isFormValid) { this.$message.warning('请填写完整的赛程信息'); return }
      
      // 双方不可相同
      if(this.scheduleForm.team1_id === this.scheduleForm.team2_id){ this.$message.warning('两支参赛球队不能相同'); return }
      
      // 构造符合后端要求的数据格式
      let matchData = {
        matchName: this.scheduleForm.match_name,
        matchTime: this.scheduleForm.date, // 将date字段改为matchTime
        homeTeamId: this.scheduleForm.team1_id,
        awayTeamId: this.scheduleForm.team2_id,
        location: this.scheduleForm.location,
        competitionId: this.matchType, // 传入 competitionId
        tournamentId: this.tournamentId // 优先使用传入的 tournamentId
      };
      
      console.log('[ScheduleInput] Submitting matchData:', matchData, 'this.matchType:', this.matchType);

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
        this.scheduleForm = { match_name: '', team1_id: null, team2_id: null, date: '', location: '', tournament_id: null };
  } catch{ 
        this.$message.error('创建比赛异常')
      } finally {
        this.submitting = false;
      }
    },
    
    // 根据比赛类型获取赛事ID
    getTournamentIdByMatchType(matchType) {
      // 如果是数字ID，直接返回
      if (typeof matchType === 'number' || !isNaN(Number(matchType))) {
        return Number(matchType);
      }
      // 尝试从已加载的赛事列表中查找
      if (this.tournaments && this.tournaments.length > 0) {
        const comp = this.tournaments.find(t => t.name === matchType);
        if (comp) return comp.id;
      }
      return 1; // 默认回退
    },
    getMatchTypeLabel() {
      if (!this.matchType) return '';
      // 尝试通过ID查找名称
      if (this.tournaments && this.tournaments.length > 0) {
        const comp = this.tournaments.find(t => t.id == this.matchType);
        if (comp) return comp.name;
      }
      // 如果找不到或matchType本身就是名称，直接返回
      return String(this.matchType);
    },
    async loadTournaments(){
      this.tournamentsLoading = true
      try{
        const { ok, data, error } = await fetchTournaments({ force:true })
        if(ok){ 
          const all = Array.isArray(data)? data : [] 
          // 如果传入了 matchType (competitionId)，则进行过滤
          if(this.matchType) {
            this.tournaments = all.filter(t => t.competitionId == this.matchType)
            // 如果只有一个选项，自动选中
            if(this.tournaments.length === 1 && !this.scheduleForm.tournamentId) {
              this.scheduleForm.tournamentId = this.tournaments[0].id
            }
          } else {
            this.tournaments = all
          }
        }
        else { this.$message.info(error?.message || '无法加载赛事实例列表'); this.tournaments = [] }
      }catch{ this.tournaments = [] }
      finally{ this.tournamentsLoading = false }
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