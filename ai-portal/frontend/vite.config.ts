// Vite 构建配置
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
// Element Plus 按需引入插件
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
// 路径解析
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    // Vue3 插件
    vue(),
    // Element Plus API 自动按需引入（如 ElMessage, ElNotification）
    AutoImport({
      resolvers: [ElementPlusResolver()],
      // 自动导入 Vue 相关函数
      imports: ['vue', 'vue-router', 'pinia'],
      // 生成自动导入声明文件
      dts: 'src/auto-imports.d.ts',
    }),
    // Element Plus 组件自动按需引入
    Components({
      resolvers: [ElementPlusResolver()],
      // 生成组件自动导入声明文件
      dts: 'src/components.d.ts',
    }),
  ],

  // 路径别名配置
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },

  // 开发服务器配置
  server: {
    port: 3000,
    // 代理配置：开发时将 /api 请求代理到后端服务
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        configure: (proxy) => {
          proxy.on('proxyRes', (proxyRes, req, res) => {
            // Follow redirects internally instead of passing them to the browser
            if (proxyRes.statusCode === 301 || proxyRes.statusCode === 302 || proxyRes.statusCode === 307 || proxyRes.statusCode === 308) {
              const location = proxyRes.headers.location
              if (location) {
                // Rewrite the redirect to go through the proxy
                const newLocation = location.replace(/^http:\/\/localhost:8000/, '')
                proxyRes.headers.location = newLocation
              }
            }
          })
        },
      },
      '/uploads': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path,
      },
    },
  },

  // 构建优化配置
  build: {
    // chunk 大小警告限制（单位：kb）
    chunkSizeWarningLimit: 1000,
    // Rollup 分包策略
    rollupOptions: {
      output: {
        // 自定义分包：将第三方库拆分，利用浏览器缓存
        manualChunks: {
          // Vue 核心全家桶
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          // Element Plus 组件库
          'element-plus': ['element-plus', '@element-plus/icons-vue'],
          // ECharts 图表库
          'echarts': ['echarts'],
          // Markdown 渲染相关
          'markdown': ['markdown-it', 'highlight.js'],
          // 工具库
          'utils': ['axios', 'dayjs'],
        },
        // 文件命名策略：使用内容hash实现长期缓存
        chunkFileNames: 'js/[name]-[hash].js',
        entryFileNames: 'js/[name]-[hash].js',
        assetFileNames: '[ext]/[name]-[hash].[ext]',
      },
    },
    // 启用 CSS 代码拆分
    cssCodeSplit: true,
    // 生产环境移除 console
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
  },

  // CSS 配置
  css: {
    preprocessorOptions: {
      scss: {
        // Element Plus 主题变量覆盖入口
        additionalData: `@use "@/assets/styles/element-vars.scss" as *;`,
      },
    },
  },
})
