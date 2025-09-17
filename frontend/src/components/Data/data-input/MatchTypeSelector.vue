<template>
  <el-card class="match-type-card" shadow="hover" ref="matchTypeCard">
    <template #header>
      <div class="card-header">
        <div class="card-title">
          <el-icon><Trophy /></el-icon>
          选择比赛类型
        </div>
        <div v-if="currentMatchType" class="header-right">
          <el-tag :type="getMatchTypeTagType(currentMatchType)" class="current-type-tag" effect="dark">
            {{ getMatchTypeLabel() }}
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
              placeholder="选择比赛类型"
              class="type-selector"
              @change="onChange"
              popper-class="match-type-dropdown"
              clearable
            >
              <el-option value="champions-cup" :label="getMatchTypeLabel('champions-cup')">
                <div class="option-content">
                  <el-icon class="option-icon"><Trophy /></el-icon>
                  <div class="option-info">
                    <div class="option-name">冠军杯</div>
                    <div class="option-desc">高水平淘汰制赛事</div>
                  </div>
                </div>
              </el-option>
              <el-option value="womens-cup" :label="getMatchTypeLabel('womens-cup')">
                <div class="option-content">
                  <el-icon class="option-icon"><UserFilled /></el-icon>
                  <div class="option-info">
                    <div class="option-name">女子杯</div>
                    <div class="option-desc">女子赛事记录</div>
                  </div>
                </div>
              </el-option>
              <el-option value="eight-a-side" :label="getMatchTypeLabel('eight-a-side')">
                <div class="option-content">
                  <el-icon class="option-icon"><Calendar /></el-icon>
                  <div class="option-info">
                    <div class="option-name">八人制</div>
                    <div class="option-desc">常规小场赛事</div>
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
import { reactive, computed } from 'vue'
import { Trophy, UserFilled, Calendar } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  // 支持父级 kebab-case 传入 (get-match-type-label / get-match-type-tag-type)
  getMatchTypeLabel: { type: Function, required: true },
  getMatchTypeTagType: { type: Function, required: true }
})
const emit = defineEmits(['update:modelValue','change'])

const form = reactive({ matchType: props.modelValue })

function onChange(val){
  emit('update:modelValue', val)
  emit('change', val)
}

const currentMatchType = computed(()=> form.matchType)
</script>
