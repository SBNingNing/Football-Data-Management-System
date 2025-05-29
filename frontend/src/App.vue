<template>
  <div class="app-container">
    <el-container v-if="isAuthenticated">
      <el-aside width="200px">
        <AppSidebar />
      </el-aside>
      <el-container>
        <el-header>
          <AppHeader />
        </el-header>
        <el-main>
          <router-view />
        </el-main>
        <el-footer>
          <AppFooter />
        </el-footer>
      </el-container>
    </el-container>

    <div v-else>
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useUserStore } from './store/modules/user';
import AppHeader from './components/common/AppHeader.vue';
import AppSidebar from './components/common/AppSidebar.vue';
import AppFooter from './components/common/AppFooter.vue';

const userStore = useUserStore();
const isAuthenticated = computed(() => userStore.isAuthenticated);
</script>

<style scoped>
.app-container {
  min-height: 100vh;
}

.el-header {
  background-color: #fff;
  border-bottom: 1px solid #eee;
  padding: 0;
  line-height: 60px;
}

.el-aside {
  background-color: #304156;
  color: #fff;
}

.el-footer {
  background-color: #f4f4f5;
  color: #333;
  text-align: center;
  padding: 20px;
}

.el-main {
  background-color: #f5f7fa;
  padding: 20px;
}
</style>
