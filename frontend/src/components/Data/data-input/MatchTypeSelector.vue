<template>
  <el-card class="match-type-card" shadow="hover" ref="matchTypeCard">
    <template #header>
      <div class="card-header">
        <div class="card-title">
          <el-icon><Trophy /></el-icon>
          选择赛事类型
        </div>
        <div v-if="currentMatchType" class="header-right">
          <el-tag type="primary" class="current-type-tag" effect="dark">
            {{ getSelectedLabel() }}
          </el-tag>
        </div>
      </div>
    </template>
    <div class="match-type-content">
      <div class="type-selector-wrapper">
        <el-form :model="form" label-width="0">
          <el-form-item>
            <el-select
              v-model="form.matchType"
              placeholder="选择赛事类型"
              class="type-selector"
              @change="onChange"
              popper-class="match-type-dropdown"
              clearable
            >
              <el-option 
                v-for="comp in competitions" 
                :key="comp.id" 
                :label="comp.name" 
                :value="comp.id"
              >
                <div class="option-content">
                  <el-icon class="option-icon"><Trophy /></el-icon>
                  <div class="option-info">
                    <div class="option-name">{{ comp.name }}</div>
                  </div>
                </div>
              </el-option>
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      <slot name="stats"></slot>
    </div>
  </el-card>
</template>
<script setup>
import { reactive, computed, ref, onMounted, watch } from 'vue'
import { Trophy } from '@element-plus/icons-vue'
import { fetchCompetitions } from '@/domain/competition/competitionsService'

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  getMatchTypeLabel: { type: Function, default: () => {} },
  getMatchTypeTagType: { type: Function, default: () => {} }
})
const emit = defineEmits(['update:modelValue','change'])

const form = reactive({ matchType: props.modelValue })
const competitions = ref([])

// 监听 props.modelValue 变化，保持内部状态同步
watch(() => props.modelValue, (newVal) => {
  if (newVal !== form.matchType) {
    form.matchType = newVal
  }
})

function onChange(val){
  console.log('[MatchTypeSelector] onChange:', val)
  emit('update:modelValue', val)
  emit('change', val)
}

const currentMatchType = computed(()=> form.matchType)

const getSelectedLabel = () => {
  if (!currentMatchType.value) return ''
  const comp = competitions.value.find(c => c.id === currentMatchType.value)
  return comp ? comp.name : (props.getMatchTypeLabel(currentMatchType.value) || currentMatchType.value)
}

onMounted(async () => {
  try {
    const { ok, data } = await fetchCompetitions()
    if (ok) {
      competitions.value = data.competitions || []
      console.log('[MatchTypeSelector] Competitions loaded:', competitions.value)
    }
  } catch (e) {
    console.error('Failed to load competitions', e)
  }
})
</script>
