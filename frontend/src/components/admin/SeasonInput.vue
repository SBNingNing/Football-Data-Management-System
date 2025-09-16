<template>
  <el-card class="form-card season-input-card">
    <template #header>
      <div class="form-header">
        <h3 class="form-title">
          <el-icon class="form-icon"><Calendar /></el-icon>
          赛季录入
        </h3>
      </div>
    </template>
    <el-form :model="form" label-width="100px" class="season-form">
      <el-form-item label="名称">
        <el-input v-model="form.name" placeholder="赛季名称，如 2024-2025" />
      </el-form-item>
      <el-form-item label="开始时间">
        <el-date-picker v-model="form.startDate" type="date" placeholder="选择开始日期" style="width:100%;" />
      </el-form-item>
      <el-form-item label="结束时间">
        <el-date-picker v-model="form.endDate" type="date" placeholder="选择结束日期" style="width:100%;" />
      </el-form-item>
      <el-form-item class="entity-submit-zone">
        <el-button type="primary" :disabled="!canSubmit" :loading="submitting" @click="submit">创建赛季</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { reactive, ref, computed } from 'vue'
import { Calendar } from '@element-plus/icons-vue'
import { createSeason, SEASON_CACHE_KEYS } from '@/domain/season/seasonsService'
import { mutateAndInvalidate } from '@/domain/common/mutation'
import notify from '@/utils/notify'

const emit = defineEmits(['submit'])

const form = reactive({ name: '', startDate: '', endDate: '' })
const submitting = ref(false)

const canSubmit = computed(()=> !!form.name && !!form.startDate && !!form.endDate && !submitting.value)

function normalizeDates(payload){
  const toISO = (d) => {
    if(!d) return ''
    if(typeof d === 'string') return d
    try { return new Date(d).toISOString().slice(0,10) } catch { return '' }
  }
  return { ...payload, startDate: toISO(payload.startDate), endDate: toISO(payload.endDate) }
}

function reset(){ form.name=''; form.startDate=''; form.endDate='' }

function submit(){
  if(!canSubmit.value) return
  submitting.value = true
  mutateAndInvalidate(
    () => createSeason(normalizeDates(form)),
    {
      invalidate: [SEASON_CACHE_KEYS.LIST],
      onSuccess: (data) => { notify.success('赛季创建成功'); emit('submit', data); reset() },
      invalidatePrefixes: ['stats:'],
    }
  ).finally(()=>{ submitting.value=false })
}
</script>

<style scoped>
.season-input-card { margin-bottom: 16px; }
.season-form { max-width: 480px; }
.form-header { display:flex; align-items:center; }
.form-title { display:flex; align-items:center; font-size:16px; font-weight:600; margin:0; }
.form-icon { margin-right:6px; color:#409eff; }
</style>
