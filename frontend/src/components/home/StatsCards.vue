<template>
  <el-row :gutter="20" class="stats-section">
    <el-col :span="8">
      <el-card shadow="hover" class="stats-card">
        <div class="stats-card-inner">
          <i class="el-icon-data-line stats-icon"></i>
          <div class="stats-info">
            <div class="stats-number">{{ statsData.totalMatches }}</div>
            <div class="stats-label">总比赛数</div>
          </div>
        </div>
      </el-card>
    </el-col>

    <el-col :span="8">
      <el-card shadow="hover" class="stats-card">
        <div class="stats-card-inner">
          <i class="el-icon-timer stats-icon"></i>
          <div class="stats-info">
            <div class="stats-number">{{ statsData.upcomingMatches }}</div>
            <div class="stats-label">即将进行</div>
          </div>
        </div>
      </el-card>
    </el-col>

    <el-col :span="8">
      <el-card shadow="hover" class="stats-card">
        <div class="stats-card-inner">
          <i class="el-icon-finished stats-icon"></i>
          <div class="stats-info">
            <div class="stats-number">{{ statsData.completedMatches }}</div>
            <div class="stats-label">已完成赛事</div>
          </div>
        </div>
      </el-card>
    </el-col>
  </el-row>
</template>

<script>
export default {
  name: 'StatsCards',
  props: {
    statsData: {
      type: Object,
      default: () => ({
        totalMatches: 0,
        upcomingMatches: 0,
        completedMatches: 0
      })
    }
  }
};
</script>

<style scoped>
.stats-section {
  margin-bottom: 20px;
}

.stats-card {
  background-color: #f7f8fa;
  border: none;
  height: 100px;
}

.stats-card-inner {
  display: flex;
  align-items: center;
  height: 100%;
}

.stats-icon {
  font-size: 40px;
  color: #409EFF;
  margin-right: 15px;
}

.stats-info {
  display: flex;
  flex-direction: column;
}

.stats-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stats-label {
  font-size: 14px;
  color: #909399;
}
</style>
