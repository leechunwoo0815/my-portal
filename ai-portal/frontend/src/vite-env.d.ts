/// <reference types="vite/client" />

declare module '@milkdown/crepe' {
  export class Crepe {
    constructor(config: { root: HTMLElement | string; defaultValue?: string; features?: any; featureConfigs?: any })
    editor: any
    create(): Promise<void>
    destroy(): void
    getMarkdown(): string
    on(fn: (api: any) => void): this
  }
}

declare module '@milkdown/kit/plugin/listener' {
  export interface ListenerManager {
    markdownUpdated(cb: (ctx: any, markdown: string, prevMarkdown?: string) => void): ListenerManager
    beforeMount(cb: (ctx: any) => void): ListenerManager
    mounted(cb: (ctx: any) => void): ListenerManager
    updated(cb: (ctx: any) => void): ListenerManager
    blur(cb: (ctx: any) => void): ListenerManager
    focus(cb: (ctx: any) => void): ListenerManager
    destroy(cb: (ctx: any) => void): ListenerManager
  }
}

declare module 'element-plus/es/components/upload/index' {
  import { DefineComponent } from 'vue'
  const ElUpload: DefineComponent<{}>
  export default ElUpload
}
