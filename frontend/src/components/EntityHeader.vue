<template>
  <!-- 通用实体详情头部组件：提供标题、返回按钮、元信息(meta)与统计(stats)插槽 -->
  <div class="entity-header" :class="[`entity-header--${variant}`]">
    <div class="entity-header__back" v-if="showBack">
            <el-button
              type="primary"
              plain
              @click="onBackClick"
              class="entity-header__back-btn"
            >
              <el-icon style="margin-right:4px"><ArrowLeft /></el-icon>{{ backText }}
            </el-button>
    </div>
    <h1 class="entity-header__title">{{ title }}</h1>

    <!-- Meta 信息插槽（如学号、参与队伍数等） -->
    <div class="entity-header__meta" v-if="$slots.meta">
      <slot name="meta" />
    </div>

    <!-- 统计卡片区域 -->
    <div class="entity-header__stats" v-if="$slots.stats">
      <slot name="stats" />
    </div>
  </div>
</template>

<script>
// 说明：
//  - title: 实体名称（球员/球队/赛事）
//  - showBack: 是否显示返回按钮
//  - back 事件：点击返回按钮向父级抛出（由父页面决定路由行为）
//  - variant: 渐变主题，用于统一风格，可继续扩展
//  - 插槽：meta（元信息行），stats（统计卡片区）
import { ArrowLeft } from '@element-plus/icons-vue'

export default {
  name: 'EntityHeader',
  components: { ArrowLeft },
  props: {
    title: { type: String, default: '' },
    showBack: { type: Boolean, default: true },
    backText: { type: String, default: '返回' },
    variant: { type: String, default: 'blue' }, // blue | green | orange 等扩展
  },
  emits: ['back'],
  methods: {
    onBackClick() { this.$emit('back') }
  }
}
</script>

<style scoped>
/* 结构类命名采用 BEM，方便后续主题或尺寸层扩展 */
.entity-header {
  position: relative;
  padding: 30px 20px 40px;
  text-align: center;
  border-radius: 8px;
  color: #fff;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
/* 主题梯度，可按需追加 */
.entity-header--blue { background: linear-gradient(135deg,#1e88e5 0%,#1976d2 100%); }
.entity-header--green { background: linear-gradient(135deg,#2ecc71 0%,#27ae60 100%); }
.entity-header--orange { background: linear-gradient(135deg,#fb8c00 0%,#ef6c00 100%); }

.entity-header__back { position: absolute; top: 20px; left: 20px; }
.entity-header__back-btn { background-color: rgba(255,255,255,0.12); border-color: rgba(255,255,255,0.3); }
.entity-header__back-btn:hover { background-color: rgba(255,255,255,0.22); }

.entity-header__title { margin: 0 0 18px; font-size: 36px; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.25); }
/* 元信息区：可换行 */
.entity-header__meta { display: flex; justify-content: center; gap: 30px; flex-wrap: wrap; margin-top: 8px; }
/* 统计卡片区 */
.entity-header__stats { margin-top: 26px; display: flex; justify-content: center; flex-wrap: wrap; gap: 24px; }

@media (max-width: 640px) {
  .entity-header { padding: 24px 16px 32px; }
  .entity-header__title { font-size: 28px; }
  .entity-header__meta { gap: 16px; }
  .entity-header__stats { gap: 16px; }
}
</style>
