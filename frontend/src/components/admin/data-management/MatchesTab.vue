<template>
  <el-card class="manage-card">
    <template #header>
      <div class="card-header">
        <span>比赛管理</span>
        <div class="header-stats">共 {{ total }} 场比赛</div>
      </div>
    </template>

    <!-- 搜索区域 -->
    <div class="search-section">
      <slot name="search" />
    </div>

    <!-- 列表 / 空状态 -->
    <div class="cards-container">
      <div v-if="items.length === 0" class="no-data">
        <el-empty description="暂无比赛数据" />
      </div>
      <el-row :gutter="20" v-else>
        <el-col :span="8" v-for="match in items" :key="match.id || match.matchId">
          <slot name="card" :match="match" />
        </el-col>
      </el-row>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper" v-if="total > pageSize">
      <el-pagination
        v-model:current-page="currentPageProxy"
        v-model:page-size="pageSizeProxy"
        :page-sizes="[9,18,36]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
      />
    </div>
  </el-card>
</template>
<script setup>
import { computed } from 'vue'
/**
 * MatchesTab 组件（展示层）
 * Props:
 *  - items: 比赛数组 (已分页切片)
 *  - total: 过滤后比赛总数，用于显示统计与分页 total
 *  - currentPage: 当前页 (父级通过 v-model:current-page 双向绑定)
 *  - pageSize: 每页数量 (父级通过 v-model:page-size 双向绑定)
 * Emits:
 *  - update:currentPage(number)
 *  - update:pageSize(number)
 * Slots:
 *  - search: 顶部搜索与筛选区域
 *  - card:   单个比赛卡片渲染 (作用域 { match })
 * 组件不关心数据来源与业务事件 (编辑/删除/完赛)；这些事件由父组件在 slot 内容内部直接透传 emit。
 */
const props = defineProps({
  items: { type: Array, default: () => [] },
  total: { type: Number, default: 0 },
  currentPage: { type: Number, default: 1 },
  pageSize: { type: Number, default: 9 }
})
const emit = defineEmits(['update:currentPage','update:pageSize'])
const currentPageProxy = computed({
  get: ()=> props.currentPage,
  set: v => emit('update:currentPage', v)
})
const pageSizeProxy = computed({
  get: ()=> props.pageSize,
  set: v => emit('update:pageSize', v)
})
</script>
