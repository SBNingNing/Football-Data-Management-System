<template>
  <el-card class="form-card tournament-quick-input-card">
    <template #header>
      <div class="form-header">
        <h3 class="form-title">
          <el-icon class="form-icon"><Collection /></el-icon>
          赛事实例快速创建
        </h3>
      </div>
    </template>
    <el-form :model="form" label-width="110px" class="tournament-quick-form">
      <el-form-item label="赛事ID或名称">
        <el-input v-model="form.competition_id" placeholder="请输入赛事ID或赛事名称" />
      </el-form-item>
      <el-form-item label="赛季ID或名称">
        <el-input v-model="form.season_id" placeholder="请输入赛季ID或赛季名称(如: 2024-2025)" />
      </el-form-item>
      <el-form-item label="试运行模式">
        <el-switch v-model="form.dryRun" />
      </el-form-item>
      <el-form-item class="entity-submit-zone">
        <el-button type="primary" :disabled="!canSubmit" :loading="submitting" @click="submit">{{ form.dryRun ? '试运行' : '创建赛事实例' }}</el-button>
      </el-form-item>
    </el-form>
    <div v-if="response" class="quick-result">
      <pre class="result-json">{{ response }}</pre>
    </div>
  </el-card>
</template>

<script setup>
import { reactive, ref, computed } from 'vue'
import { Collection } from '@element-plus/icons-vue'
import { quickCreateTournamentInstance, TOURNAMENT_CACHE_KEYS } from '@/domain/tournament/tournamentCrudService'
import { mutateAndInvalidate } from '@/domain/common/mutation'
import notify from '@/utils/notify'

const emit = defineEmits(['submit'])

const form = reactive({ competition_id: '', season_id: '', dryRun: true })
const submitting = ref(false)
const response = ref(null)

const canSubmit = computed(()=> !!form.competition_id && !!form.season_id && !submitting.value)

function reset(){ form.competition_id=''; form.season_id=''; form.dryRun=true }

function submit(){
  if(!canSubmit.value) return
  submitting.value = true
  mutateAndInvalidate(
    () => quickCreateTournamentInstance({ ...form }),
    {
      invalidate: [TOURNAMENT_CACHE_KEYS.LIST],
      invalidatePrefixes: ['tournament:','stats:'],
      onSuccess: (data) => {
        response.value = JSON.stringify(data, null, 2)
        notify.success(form.dryRun ? '试运行成功' : '赛事实例创建成功')
        emit('submit', data)
        if(!form.dryRun) reset()
      }
    }
  ).finally(()=>{ submitting.value=false })
}
</script>

<style scoped>
.tournament-quick-input-card { margin-bottom:16px; }
.tournament-quick-form { max-width:520px; }
.form-header { display:flex; align-items:center; }
.form-title { display:flex; align-items:center; font-size:16px; font-weight:600; margin:0; }
.form-icon { margin-right:6px; color:#67c23a; }
.quick-result { margin-top:12px; background:#f5f7fa; border:1px solid #e4e7ed; border-radius:4px; padding:8px; }
.result-json { font-size:12px; line-height:1.4; white-space:pre-wrap; word-break:break-word; margin:0; }
</style>