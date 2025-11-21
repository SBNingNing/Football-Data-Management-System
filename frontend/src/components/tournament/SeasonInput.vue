<template>
  <el-card class="season-input-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span class="card-title">添加赛季</span>
      </div>
    </template>
    
    <el-form 
      ref="seasonFormRef" 
      :model="seasonForm" 
      :rules="seasonRules" 
      label-width="80px"
      size="small"
    >
      <el-form-item label="赛季名称" prop="name">
        <el-input 
          v-model="seasonForm.name" 
          placeholder="请输入赛季名称，如：2024-2025赛季"
          maxlength="20"
          show-word-limit
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="开始时间" prop="start_time">
        <el-date-picker
          v-model="seasonForm.start_time"
          type="date"
          placeholder="选择开始日期"
          style="width: 100%"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>

      <el-form-item label="结束时间" prop="end_time">
        <el-date-picker
          v-model="seasonForm.end_time"
          type="date"
          placeholder="选择结束日期"
          style="width: 100%"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>
      
      <el-form-item class="form-actions">
        <el-button 
          type="primary" 
          @click="submitSeason" 
          :loading="submitting"
        >
          <el-icon><Plus /></el-icon>
          添加赛季
        </el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { Plus } from '@element-plus/icons-vue'
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { createSeason } from '@/domain/season/seasonsService'
import '@/assets/styles/input-components.css'

const emit = defineEmits(['submit'])
const seasonFormRef = ref()
const submitting = ref(false)

const seasonForm = reactive({
  name: '',
  start_time: '',
  end_time: ''
})

const seasonRules = {
  name: [
    { required: true, message: '请输入赛季名称', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  start_time: [
    { required: true, message: '请选择开始时间', trigger: 'change' }
  ],
  end_time: [
    { required: true, message: '请选择结束时间', trigger: 'change' }
  ]
}

const submitSeason = async () => {
  if (!seasonFormRef.value) return
  
  await seasonFormRef.value.validate(async (valid, fields) => {
    if (valid) {
      try {
        submitting.value = true
        
        await createSeason(seasonForm)
        ElMessage.success('赛季添加成功')
        
        // 重置表单
        seasonFormRef.value.resetFields()
        
        // 通知父组件刷新数据
        emit('submit')
      } catch (error) {
        console.error('添加赛季失败:', error)
        ElMessage.error('添加赛季失败：' + (error.message || '未知错误'))
      } finally {
        submitting.value = false
      }
    } else {
      console.error('表单验证失败:', fields)
    }
  })
}
</script>