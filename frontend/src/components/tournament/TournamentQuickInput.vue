<template>
  <el-card class="input-component-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span class="card-title">创建赛季赛事</span>
      </div>
    </template>
    
    <el-form 
      ref="tournamentFormRef" 
      :model="tournamentForm" 
      :rules="tournamentRules" 
      label-width="80px"
      size="small"
    >
      <el-form-item label="赛事名称" prop="competition_id">
        <el-select 
          v-model="tournamentForm.competition_id" 
          placeholder="选择赛事" 
          style="width: 100%"
          clearable
        >
          <el-option 
            v-for="comp in competitions" 
            :key="comp.id" 
            :label="comp.name" 
            :value="comp.id"
          />
        </el-select>
      </el-form-item>
      
      <el-form-item label="所属赛季" prop="season_id">
        <el-select 
          v-model="tournamentForm.season_id" 
          placeholder="选择所属赛季" 
          style="width: 100%"
          clearable
        >
          <el-option 
            v-for="season in seasons" 
            :key="season.id" 
            :label="season.name" 
            :value="season.id"
          />
        </el-select>
      </el-form-item>
      
      <el-form-item class="form-actions">
        <el-button 
          type="primary" 
          @click="submitTournament" 
          :loading="submitting"
        >
          <el-icon><Plus /></el-icon>
          创建赛季赛事
        </el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { Plus } from '@element-plus/icons-vue'
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { createTournament } from '@/api/tournaments'
import { fetchSeasons } from '@/api/seasons'
import { fetchCompetitions } from '@/api/competitions'
import '@/assets/styles/input-components.css'

const emit = defineEmits(['submit'])
const seasons = ref([])
const competitions = ref([])
const submitting = ref(false)
const tournamentFormRef = ref()

const tournamentForm = reactive({
  competition_id: '',
  season_id: ''
})

const tournamentRules = {
  competition_id: [
    { required: true, message: '请选择赛事', trigger: 'change' }
  ],
  season_id: [
    { required: true, message: '请选择所属赛季', trigger: 'change' }
  ]
}

const submitTournament = async () => {
  if (!tournamentFormRef.value) return
  
  await tournamentFormRef.value.validate(async (valid, fields) => {
    if (valid) {
      try {
        submitting.value = true
        
        await createTournament(tournamentForm)
        ElMessage.success('赛季赛事创建成功')
        
        // 重置表单
        tournamentFormRef.value.resetFields()
        
        // 通知父组件刷新数据
        emit('submit')
      } catch (error) {
        console.error('创建赛季赛事失败:', error)
        ElMessage.error('创建赛季赛事失败：' + (error.message || '未知错误'))
      } finally {
        submitting.value = false
      }
    } else {
      console.error('表单验证失败:', fields)
    }
  })
}

// 加载赛季列表
const loadSeasons = async () => {
  try {
    const { ok, data } = await fetchSeasons()
    if (ok) {
      const rawList = data?.data || data || []
      seasons.value = rawList.map(normalizeSeason)
    }
  } catch (error) {
    console.error('加载赛季列表失败:', error)
  }
}

// 加载赛事列表
const loadCompetitions = async () => {
  try {
    const { ok, data } = await fetchCompetitions()
    if (ok) {
      const rawData = data?.data || data || {}
      const list = rawData.competitions || []
      competitions.value = list.map(normalizeCompetition)
    }
  } catch (error) {
    console.error('加载赛事列表失败:', error)
  }
}

onMounted(() => {
  loadSeasons()
  loadCompetitions()
})
</script>