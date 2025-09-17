<template>
  <el-card class="form-card competition-input-card">
    <template #header>
      <div class="form-header">
        <h3 class="form-title">
          <el-icon class="form-icon"><Trophy /></el-icon>
          赛事录入
        </h3>
      </div>
    </template>
    <el-form :model="form" label-width="80px" class="competition-form">
      <el-form-item label="名称">
        <el-input v-model="form.name" placeholder="赛事名称，如 校园杯" />
      </el-form-item>
      <el-form-item class="entity-submit-zone">
        <el-button type="primary" :disabled="!canSubmit" :loading="submitting" @click="submit">创建赛事</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { reactive, ref, computed } from 'vue'
import { Trophy } from '@element-plus/icons-vue'
import { createCompetition, COMPETITION_CACHE_KEYS } from '@/domain/competition/competitionsService'
import { mutateAndInvalidate } from '@/domain/common/mutation'
import notify from '@/utils/notify'

const emit = defineEmits(['submit'])

const form = reactive({ name: '' })
const submitting = ref(false)
const canSubmit = computed(()=> !!form.name && !submitting.value)

function reset(){ form.name='' }

function submit(){
  if(!canSubmit.value) return
  submitting.value = true
  mutateAndInvalidate(
    () => createCompetition({ name: form.name }),
    {
      invalidate: [COMPETITION_CACHE_KEYS.list({})],
      invalidatePrefixes: ['tournaments:','stats:'],
      onSuccess: (data)=>{ notify.success('赛事创建成功'); emit('submit', data); reset() }
    }
  ).finally(()=>{ submitting.value=false })
}
</script>

<style scoped>
.competition-input-card { margin-bottom:16px; }
.competition-form { max-width:420px; }
.form-header { display:flex; align-items:center; }
.form-title { display:flex; align-items:center; font-size:16px; font-weight:600; margin:0; }
.form-icon { margin-right:6px; color:#e6a23c; }
</style>
