// 环境类型声明文件
/// <reference types="vite/client" />

// 声明 .vue 文件模块，使 TypeScript 能识别 Vue 单文件组件
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// 声明 markdown-it 模块
declare module 'markdown-it' {
  import MarkdownIt from 'markdown-it'
  export default MarkdownIt
}

// 环境变量类型声明
interface ImportMetaEnv {
  // API 基础地址
  readonly VITE_API_BASE_URL: string
  // 应用标题
  readonly VITE_APP_TITLE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
