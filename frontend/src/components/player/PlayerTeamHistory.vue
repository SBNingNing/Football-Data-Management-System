<template>
  <div class="player-team-history-card">
    <h3 class="card-header">球员队伍历史</h3>
    <div class="history-list">
      <template v-if="teamHistories && teamHistories.length > 0">
        <div v-for="(item, index) in teamHistories" :key="index" class="history-item">
          <div class="history-season">{{ item.season_name || '未知赛季' }}</div>
          <div class="history-details">
            <div class="team-name">{{ item.team_name || '未知队伍' }}</div>
            <div class="meta-tags">
              <span class="tag tournament">{{ item.tournament_name || '未知赛事' }}</span>
              <span class="tag number" v-if="item.player_number !== null && item.player_number !== undefined">
                #{{ item.player_number }}
              </span>
            </div>
          </div>
        </div>
      </template>
      <template v-else>
        <div class="history-empty">暂无球员队伍历史记录</div>
      </template>
    </div>
  </div>
</template>

<script setup>
defineProps({
  teamHistories: {
    type: Array,
    default: () => []
  }
});
</script>

<style scoped>
.player-team-history-card {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
}

.card-header {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2d3748;
  padding-bottom: 12px;
  margin-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.history-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 6px;
  transition: background-color 0.2s ease-in-out;
}

.history-item:hover {
  background-color: #f7fafc;
}

.history-season {
  font-weight: 500;
  color: #718096;
  width: 100px;
  flex-shrink: 0;
}

.history-details {
  flex-grow: 1;
}

.team-name {
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 6px;
}

.meta-tags {
  display: flex;
  gap: 8px;
}

.tag {
  font-size: 0.75rem;
  padding: 3px 8px;
  border-radius: 9999px;
  font-weight: 500;
}

.tag.tournament {
  background-color: #ebf8ff;
  color: #3182ce;
}

.tag.number {
  background-color: #f0fff4;
  color: #38a169;
}

.history-empty {
  color: #a0aec0;
  padding: 20px;
  text-align: center;
  background-color: #f7fafc;
  border-radius: 6px;
}
</style>