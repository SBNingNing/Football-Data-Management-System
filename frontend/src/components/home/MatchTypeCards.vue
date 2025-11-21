<template>
  <el-row :gutter="20" class="match-types">
    <el-col :span="8" v-for="comp in competitions" :key="comp.competition_id">
      <el-card shadow="hover" @click="navigateToTournament(comp.competition_id)" class="clickable-card">
        <div class="match-type-card">
          <el-icon class="card-icon"><Trophy /></el-icon>
          <h3>{{ comp.name }}</h3>
          <p>查看{{ comp.name }}详情</p>
        </div>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { Trophy } from '@element-plus/icons-vue'
import logger from '@/utils/logger';

const props = defineProps({
  competitions: {
    type: Array,
    default: () => []
  }
})

const router = useRouter()

const navigateToTournament = (competitionId) => {
  logger.debug('点击赛事类型卡片', competitionId)
  router.push({
    path: '/tournament',
    query: { competitionId }
  })
}
</script>

<style scoped>
.match-types {
  margin-top: 20px;
}

.clickable-card {
  cursor: pointer;
}

.match-type-card {
  text-align: center;
  padding: 20px;
  transition: all 0.3s ease;
}

.clickable-card:hover .match-type-card {
  transform: translateY(-5px);
}

.card-icon {
  font-size: 40px;
  margin-bottom: 10px;
  color: #409EFF;
}

.match-type-card h3 {
  margin-bottom: 10px;
}
</style>