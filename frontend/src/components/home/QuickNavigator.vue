<template>
  <div class="quick-navigator" v-show="showNavigator">
    <div class="navigator-header">
      <el-icon class="header-icon"><Guide /></el-icon>
      <span>快速导航</span>
      <el-button 
        text 
        @click="toggleNavigator"
        :icon="isExpanded ? Minus : Plus"
        size="small"
        class="toggle-btn"
      />
    </div>
    
    <div class="navigator-content" v-show="isExpanded">
      <div class="nav-item" @click="scrollToElement('welcome')" :class="{ active: activeSection === 'welcome' }">
        <el-icon><House /></el-icon>
        <span>欢迎页面</span>
      </div>
      
      <div class="nav-item" @click="scrollToElement('featured-matches')" :class="{ active: activeSection === 'featured-matches' }">
        <el-icon><Trophy /></el-icon>
        <span>近期比赛</span>
      </div>
      
      <div class="nav-item" @click="scrollToElement('rankings')" :class="{ active: activeSection === 'rankings' }">
        <el-icon><Medal /></el-icon>
        <span>排行数据</span>
      </div>
      
      <div class="nav-item" @click="scrollToElement('match-records')" :class="{ active: activeSection === 'match-records' }">
        <el-icon><Calendar /></el-icon>
        <span>比赛记录</span>
      </div>
      
      <div class="nav-item" @click="scrollToElement('team-search')" :class="{ active: activeSection === 'team-search' }">
        <el-icon><User /></el-icon>
        <span>球队搜索</span>
      </div>
      
      <div class="nav-item" @click="scrollToElement('player-search')" :class="{ active: activeSection === 'player-search' }">
        <el-icon><UserFilled /></el-icon>
        <span>球员搜索</span>
      </div>
      
      <div class="nav-divider"></div>
      
      <div class="nav-item" @click="scrollToTop">
        <el-icon><Top /></el-icon>
        <span>返回顶部</span>
      </div>
    </div>
  </div>
</template>

<script>
import { 
  Guide, 
  House, 
  Trophy, 
  Medal, 
  Calendar, 
  User, 
  UserFilled, 
  Top,
  Plus,
  Minus 
} from '@element-plus/icons-vue'

export default {
  name: 'QuickNavigator',
  components: {
    Guide,
    House,
    Trophy,
    Medal,
    Calendar,
    User,
    UserFilled,
    Top,
    Plus, // eslint-disable-line vue/no-unused-components
    Minus // eslint-disable-line vue/no-unused-components
  },
  data() {
    return {
      showNavigator: false,
      isExpanded: true,
      activeSection: 'welcome',
      scrollTimer: null,
      Plus,
      Minus
    }
  },
  mounted() {
    this.initNavigator()
  },
  beforeUnmount() {
    this.removeScrollListener()
  },
  methods: {
    initNavigator() {
      // 延迟显示导航器
      setTimeout(() => {
        this.showNavigator = true
      }, 1000)
      
      // 添加滚动监听
      this.addScrollListener()
    },
    
    addScrollListener() {
      // 使用安全的事件监听器，防止扩展干扰
      try {
        window.addEventListener('scroll', this.handleScroll, { passive: true })
      } catch (error) {
        console.warn('滚动监听器添加失败:', error.message)
      }
    },
    
    removeScrollListener() {
      try {
        window.removeEventListener('scroll', this.handleScroll)
      } catch (error) {
        console.warn('滚动监听器移除失败:', error.message)
      }
      if (this.scrollTimer) {
        clearTimeout(this.scrollTimer)
      }
    },
    
    handleScroll() {
      // 防抖处理
      if (this.scrollTimer) {
        clearTimeout(this.scrollTimer)
      }
      
      this.scrollTimer = setTimeout(() => {
        this.updateActiveSection()
      }, 100)
    },
    
    updateActiveSection() {
      const sections = [
        { id: 'welcome', element: this.$el?.closest('.home')?.querySelector('.welcome-card') },
        { id: 'featured-matches', element: document.querySelector('.featured-matches-card') },
        { id: 'rankings', element: document.querySelector('.rankings-card') },
        { id: 'match-records', element: document.querySelector('.match-records-card') },
        { id: 'team-search', element: document.querySelector('.team-search-card') },
        { id: 'player-search', element: document.querySelector('.player-search-card') }
      ]
      
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop
      const windowHeight = window.innerHeight
      
      for (let i = sections.length - 1; i >= 0; i--) {
        const section = sections[i]
        if (section.element) {
          const rect = section.element.getBoundingClientRect()
          const elementTop = rect.top + scrollTop
          
          if (scrollTop >= elementTop - windowHeight / 2) {
            this.activeSection = section.id
            break
          }
        }
      }
    },
    
    scrollToElement(sectionId) {
      let targetElement = null
      
      switch (sectionId) {
        case 'welcome':
          targetElement = this.$el?.closest('.home')?.querySelector('.welcome-card')
          break
        case 'featured-matches':
          targetElement = document.querySelector('.featured-matches-card')
          break
        case 'rankings':
          targetElement = document.querySelector('.rankings-card')
          break
        case 'match-records':
          targetElement = document.querySelector('.match-records-card')
          break
        case 'team-search':
          targetElement = document.querySelector('.team-search-card')
          break
        case 'player-search':
          targetElement = document.querySelector('.player-search-card')
          break
      }
      
      if (targetElement) {
        const headerHeight = 60 // 考虑页面头部高度
        const elementTop = targetElement.getBoundingClientRect().top + window.pageYOffset - headerHeight
        
        window.scrollTo({
          top: elementTop,
          behavior: 'smooth'
        })
        
        // 更新激活状态
        this.activeSection = sectionId
        
        // 添加高亮效果
        this.highlightElement(targetElement)
      }
    },
    
    highlightElement(element) {
      element.style.transition = 'box-shadow 0.3s ease'
      element.style.boxShadow = '0 0 20px rgba(64, 158, 255, 0.5)'
      
      setTimeout(() => {
        element.style.boxShadow = ''
      }, 2000)
    },
    
    scrollToTop() {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      })
      this.activeSection = 'welcome'
    },
    
    toggleNavigator() {
      this.isExpanded = !this.isExpanded
    }
  }
}
</script>

<style scoped>
.quick-navigator {
  position: fixed;
  top: 20%;
  right: 20px;
  z-index: 1000;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border: 1px solid #e4e7ed;
  min-width: 160px;
  max-width: 200px;
  animation: slideInRight 0.3s ease;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.navigator-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  background: linear-gradient(135deg, #409EFF, #36A3FF);
  color: white;
  border-radius: 12px 12px 0 0;
  font-size: 14px;
  font-weight: 500;
}

.header-icon {
  margin-right: 8px;
  font-size: 16px;
}

.toggle-btn {
  margin-left: auto;
  color: white !important;
  padding: 0 !important;
  min-height: auto !important;
}

.toggle-btn:hover {
  color: #f0f0f0 !important;
}

.navigator-content {
  padding: 8px 0;
  max-height: 400px;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 13px;
  color: #606266;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background-color: #f5f7fa;
  color: #409EFF;
  border-left-color: #409EFF;
}

.nav-item.active {
  background-color: #ecf5ff;
  color: #409EFF;
  border-left-color: #409EFF;
  font-weight: 500;
}

.nav-item .el-icon {
  margin-right: 8px;
  font-size: 14px;
  flex-shrink: 0;
}

.nav-divider {
  height: 1px;
  background-color: #e4e7ed;
  margin: 8px 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .quick-navigator {
    right: 10px;
    min-width: 140px;
    max-width: 160px;
  }
  
  .navigator-header {
    padding: 10px 12px;
    font-size: 12px;
  }
  
  .nav-item {
    padding: 8px 12px;
    font-size: 12px;
  }
}

/* 滚动条样式 */
.navigator-content::-webkit-scrollbar {
  width: 4px;
}

.navigator-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 2px;
}

.navigator-content::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 2px;
}

.navigator-content::-webkit-scrollbar-thumb:hover {
  background: #a4a9b0;
}
</style>
