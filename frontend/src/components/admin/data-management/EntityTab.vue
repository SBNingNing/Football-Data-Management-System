<template>
  <el-card class="manage-card">
    <template #header>
      <div class="card-header">
        <span>{{ title }}</span>
        <div class="header-stats">
          共 {{ total }} {{ totalLabelUnit || unitLabel }}
        </div>
      </div>
    </template>

    <!-- 搜索区域交由父级使用 SearchSection 组件包装，移除内置容器以避免嵌套 -->
    <slot name="search" />

    <div class="cards-container">
      <div v-if="items.length === 0" class="no-data">
        <el-empty :description="emptyDescription" />
      </div>
      <el-row :gutter="20" v-else>
        <el-col :span="cardSpan" v-for="(item, idx) in items" :key="item.id || item._id || idx">
          <!-- 透传当前 item 统一作用域命名为 entity；同时保持兼容自定义具名解构 -->
          <slot name="card" :entity="item" :item="item" />
        </el-col>
      </el-row>
    </div>

    <div class="pagination-wrapper" v-if="total > pageSize">
      <el-pagination
        v-model:current-page="currentPageProxy"
        v-model:page-size="pageSizeProxy"
        :page-sizes="pageSizes"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
      />
    </div>
  </el-card>
</template>
<script setup>
import { computed } from 'vue'
/**
 * 通用分页列表容器 EntityTab
 * Props:
 *  - title: 标题文本
 *  - items: 当前页数据数组 (父级已切片)
 *  - total: 过滤后数据总量
 *  - unitLabel: 单位(如: 场比赛/个事件/名球员/支球队) 仅在无 totalLabelUnit 时拼接显示
 *  - totalLabelUnit: 若提供则直接使用 (例如 "场比赛")
 *  - emptyDescription: 空状态描述
 *  - cardSpan: el-col span (默认 8)
 *  - pageSizes: 可选页大小数组
 *  - currentPage / pageSize: 分页状态 (v-model:current-page, v-model:page-size)
 * Emits:
 *  - update:currentPage(number)
 *  - update:pageSize(number)
 * Slots:
 *  - search: 搜索 / 筛选区域
 *  - card: 渲染单项，作用域提供: { entity, item }
 */
const props = defineProps({
  title: { type: String, required: true },
  items: { type: Array, default: () => [] },
  total: { type: Number, default: 0 },
  unitLabel: { type: String, default: '' },
  totalLabelUnit: { type: String, default: '' },
  emptyDescription: { type: String, default: '暂无数据' },
  cardSpan: { type: Number, default: 8 },
  pageSizes: { type: Array, default: () => [9, 18, 36] },
  currentPage: { type: Number, default: 1 },
  pageSize: { type: Number, default: 9 }
})
const emit = defineEmits(['update:currentPage','update:pageSize'])
const currentPageProxy = computed({ get:()=>props.currentPage, set:v=>emit('update:currentPage', v) })
const pageSizeProxy = computed({ get:()=>props.pageSize, set:v=>emit('update:pageSize', v) })
</script>
<style scoped>
/* 使用父级已有样式类名，不再重复定义，保持轻量 */
</style>
