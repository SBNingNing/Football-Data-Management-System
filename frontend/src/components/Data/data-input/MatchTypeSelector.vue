<template>
  <el-card class="match-type-card" shadow="hover" ref="matchTypeCard">
    <template #header>
      <div class="card-header">
        <div class="card-title">
          <el-icon><Trophy /></el-icon>
          选择赛事上下文
        </div>
        <div v-if="currentMatchType && currentSeasonId" class="header-right">
          <el-tag type="primary" class="current-type-tag" effect="dark">
            {{ getSelectedLabel() }}
          </el-tag>
        </div>
      </div>
    </template>
    <div class="match-type-content">
      <div class="type-selector-wrapper">
        <el-form :model="form" label-width="80px" class="selector-form">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="赛季">
                <el-select
                  v-model="form.seasonId"
                  placeholder="选择赛季"
                  class="type-selector"
                  @change="onContextChange"
                  clearable
                >
                  <el-option
                    v-for="season in metaStore.seasons"
                    :key="season.id"
                    :label="season.name"
                    :value="season.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="赛事">
                <el-select
                  v-model="form.matchType"
                  placeholder="选择赛事类型"
                  class="type-selector"
                  @change="onContextChange"
                  clearable
                >
                  <el-option 
                    v-for="comp in metaStore.competitions" 
                    :key="comp.id" 
                    :label="comp.name" 
                    :value="comp.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </div>
      <slot name="stats"></slot>
    </div>
  </el-card>
</template>
<script setup>
import { reactive, computed, onMounted, watch } from 'vue'
import { Trophy } from '@element-plus/icons-vue'
import { useMetaStore } from '@/store/modules/meta'
import { fetchTournaments } from '@/api/tournaments'

const props = defineProps({
  modelValue: { type: [String, Number], default: '' }, // competitionId
  seasonId: { type: [String, Number], default: '' },
  getMatchTypeLabel: { type: Function, default: () => {} },
  getMatchTypeTagType: { type: Function, default: () => {} }
})
const emit = defineEmits(['update:modelValue', 'update:seasonId', 'change', 'tournament-found'])

const metaStore = useMetaStore()
const form = reactive({ 
  matchType: props.modelValue,
  seasonId: props.seasonId
})

// Sync props
watch(() => props.modelValue, (val) => form.matchType = val)
watch(() => props.seasonId, (val) => form.seasonId = val)

const currentMatchType = computed(()=> form.matchType)
const currentSeasonId = computed(()=> form.seasonId)

const getSelectedLabel = () => {
  if (!currentMatchType.value || !currentSeasonId.value) return ''
  const comp = metaStore.getCompetitionById(currentMatchType.value)
  const season = metaStore.getSeasonById(currentSeasonId.value)
  return `${season?.name || ''} - ${comp?.name || ''}`
}

async function onContextChange() {
  emit('update:modelValue', form.matchType)
  emit('update:seasonId', form.seasonId)
  emit('change', form.matchType)

  if (form.matchType && form.seasonId) {
    // Fetch Tournament ID
    try {
      const res = await fetchTournaments({ 
        competition_id: form.matchType, 
        season_id: form.seasonId 
      })
      // 兼容后端返回结构
      const list = Array.isArray(res.data) ? res.data : (res.data?.data || [])
      
      if (list.length > 0) {
        const tournament = list[0]
        console.log('Tournament Found:', tournament)
        emit('tournament-found', tournament.id || tournament.赛事ID) // 兼容不同字段名
      } else {
        console.warn('No tournament found for this combination')
        emit('tournament-found', null)
      }
    } catch (e) {
      console.error('Error fetching tournament', e)
      emit('tournament-found', null)
    }
  } else {
    emit('tournament-found', null)
  }
}

onMounted(() => {
  metaStore.loadAll()
})
</script>
<style scoped>
.selector-form {
  width: 100%;
}
.type-selector {
  width: 100%;
}
</style>