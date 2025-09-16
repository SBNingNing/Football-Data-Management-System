<template>
  <el-row :gutter="20" class="match-types">
    <el-col :span="8">
      <el-card shadow="hover" @click="navigateToTournament('冠军杯')" class="clickable-card">
        <div class="match-type-card">
          <el-icon class="card-icon"><Trophy /></el-icon>
          <h3>冠军杯</h3>
          <p>查看冠军杯赛事信息</p>
        </div>
      </el-card>
    </el-col>

    <el-col :span="8">
      <el-card shadow="hover" @click="navigateToTournament('巾帼杯')" class="clickable-card">
        <div class="match-type-card">
          <el-icon class="card-icon"><Female /></el-icon>
          <h3>巾帼杯</h3>
          <p>查看巾帼杯赛事信息</p>
        </div>
      </el-card>
    </el-col>

    <el-col :span="8">
      <el-card shadow="hover" @click="navigateToTournament('八人制比赛')" class="clickable-card">
        <div class="match-type-card">
          <el-icon class="card-icon"><Football /></el-icon>
          <h3>八人制比赛</h3>
          <p>查看八人制赛事信息</p>
        </div>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { Trophy, Female, Football } from '@element-plus/icons-vue'
import logger from '@/utils/logger';

const router = useRouter()

const navigateToTournament = (tournamentName) => {
  logger.debug('点击赛事类型卡片:', tournamentName) // 调试用
  router.push({
    path: `/tournament/${encodeURIComponent(tournamentName)}`
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
