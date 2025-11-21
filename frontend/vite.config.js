import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import history from 'connect-history-api-fallback'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  // 静态资源处理
  publicDir: 'public',
  server: {
    // 仅本机访问，避免暴露到局域网
    host: '127.0.0.1',
    port: 3000,
    // 修复缓存问题的关键配置
    hmr: {
      overlay: true
    },
    // 强制预构建优化，避免缓存问题
    force: true,
    // 文件系统严格模式
    fs: {
      strict: false
    },
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  define: {
    // 如果需要兼容旧的 process.env 写法
    'process.env': {}
  },
  // 优化依赖预构建
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', 'axios', 'element-plus'],
    exclude: [],
    // 强制重新预构建
    force: true
  },
  // 配置历史模式路由回退
  configureServer: (server) => {
    server.middlewares.use(history({
      rewrites: [
        {
          from: /^\/(?!api|@vite|assets|favicon\.).*/,
          to: '/index.html'
        }
      ]
    }))
  },
  build: {
    rollupOptions: {
      // 确保 favicon 和其他静态资源被正确包含
      input: {
        main: resolve(__dirname, 'index.html')
      }
    }
  }
})