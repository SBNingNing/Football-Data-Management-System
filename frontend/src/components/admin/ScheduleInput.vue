<template>
  <el-card class="section-card">
    <div slot="header">
      <span>{{ getMatchTypeLabel() }}赛程录入</span>
    </div>
    <el-form ref="scheduleForm" :model="scheduleForm" label-width="120px">
      <el-form-item label="比赛名称">
        <el-input v-model="scheduleForm.matchName" placeholder="请输入比赛名称"></el-input>
      </el-form-item>
      <el-form-item label="参赛球队1">
        <el-select v-model="scheduleForm.team1" placeholder="请选择球队1">
          <el-option v-for="team in teams" :key="team.id" :label="team.teamName" :value="team.teamName"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="参赛球队2">
        <el-select v-model="scheduleForm.team2" placeholder="请选择球队2">
          <el-option v-for="team in teams" :key="team.id" :label="team.teamName" :value="team.teamName"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="比赛日期">
        <el-date-picker v-model="scheduleForm.date" type="datetime" placeholder="选择日期时间"></el-date-picker>
      </el-form-item>
      <el-form-item label="比赛地点">
        <el-input v-model="scheduleForm.location" placeholder="请输入比赛地点"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitSchedule">提交赛程信息</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script>
export default {
  name: 'ScheduleInput',
  props: {
    matchType: String,
    teams: Array
  },
  data() {
    return {
      scheduleForm: {
        matchName: '',
        team1: '',
        team2: '',
        date: '',
        location: ''
      }
    }
  },
  methods: {
    submitSchedule() {
      // 修正：将日期转为字符串并加上时区（北京时间），避免时区丢失
      let form = { ...this.scheduleForm };
      if (form.date instanceof Date) {
        // 转为北京时间字符串
        const pad = n => n < 10 ? '0' + n : n;
        const dt = new Date(form.date.getTime()); 
        form.date = `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())} ${pad(dt.getHours())}:${pad(dt.getMinutes())}:${pad(dt.getSeconds())}`;
      }
      this.$emit('submit', form);
      this.scheduleForm = { matchName: '', team1: '', team2: '', date: '', location: '' };
    },
    getMatchTypeLabel() {
      const labels = {
        'champions-cup': '冠军杯',
        'womens-cup': '巾帼杯',
        'eight-a-side': '八人制比赛'
      };
      return labels[this.matchType] || '';
    }
  }
}
</script>

<style scoped>
.section-card {
  border: 1px solid #e4e7ed;
}
</style>
