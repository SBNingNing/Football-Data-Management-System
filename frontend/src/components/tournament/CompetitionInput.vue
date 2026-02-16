<template>
  <el-card class="competition-input-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span class="card-title">添加赛事</span>
      </div>
    </template>
    
    <el-form 
      ref="competitionFormRef" 
      :model="competitionForm" 
      :rules="competitionRules" 
      label-width="80px"
      size="small"
    >
      <el-form-item label="赛事名称" prop="name">
        <el-input 
          v-model="competitionForm.name" 
          placeholder="请输入赛事名称，如：冠军杯、巾帼杯等"
          maxlength="30"
          show-word-limit
          style="width: 100%"
        />
      </el-form-item>
      
      <el-form-item class="form-actions">
        <el-button 
          type="primary" 
          @click="submitCompetition" 
          :loading="submitting"
        >
          <el-icon><Plus /></el-icon>
          添加赛事
        </el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { Plus } from '@element-plus/icons-vue'
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { createCompetition } from '@/api/competitions'
import '@/assets/styles/input-components.css'

const emit = defineEmits(['submit'])
const competitionFormRef = ref()
const submitting = ref(false)

const competitionForm = reactive({
  name: ''
})

const competitionRules = {
  name: [
    { required: true, message: '请输入赛事名称', trigger: 'blur' },
    { min: 2, max: 30, message: '长度在 2 到 30 个字符', trigger: 'blur' }
  ]
}

const submitCompetition = async () => {
  if (!competitionFormRef.value) return
  
  await competitionFormRef.value.validate(async (valid, fields) => {
    if (valid) {
      try {
        submitting.value = true
        
        await createCompetition(competitionForm)
        ElMessage.success('赛事添加成功')
        
        // 重置表单
        competitionFormRef.value.resetFields()
        
        // 通知父组件刷新数据
        emit('submit')
      } catch (error) {
        console.error('添加赛事失败:', error)
        ElMessage.error('添加赛事失败：' + (error.message || '未知错误'))
      } finally {
        submitting.value = false
      }
    } else {
      console.error('表单验证失败:', fields)
    }
  })
}

// 移除onMounted中的loadSeasons调用
</script>