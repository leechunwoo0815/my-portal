import { ref, type Ref } from 'vue'
import { Crepe } from '@milkdown/crepe'
import type { ListenerManager } from '@milkdown/kit/plugin/listener'
import '@milkdown/crepe/theme/common/style.css'
import '@milkdown/crepe/theme/frame.css'

export function useMdEditor(rootRef: Ref<HTMLElement | null>, initialValue = '') {
  let crepe: Crepe | null = null
  const markdown = ref(initialValue)
  const isReady = ref(false)
  let isInternalUpdate = false

  const create = async () => {
    if (!rootRef.value) return

    crepe = new Crepe({
      root: rootRef.value,
      defaultValue: initialValue,
      featureConfigs: {
        placeholder: {
          text: '开始写作...',
        },
      },
    })

    crepe.on((listener: ListenerManager) => {
      listener.markdownUpdated((_ctx, md) => {
        if (!isInternalUpdate) {
          markdown.value = md
        }
      })
    })

    await crepe.create()
    isReady.value = true
  }

  const setContent = async (content: string) => {
    if (!crepe || crepe.editor.status !== 'Created') return
    const currentMd = crepe.getMarkdown()
    if (content === currentMd) return

    isInternalUpdate = true
    const { replaceAll } = await import('@milkdown/kit/utils')
    crepe.editor.action(replaceAll(content || ''))
    markdown.value = content
    isInternalUpdate = false
  }

  const getMarkdown = () => {
    return crepe?.getMarkdown() || ''
  }

  const destroy = () => {
    if (crepe) {
      crepe.destroy()
      crepe = null
      isReady.value = false
    }
  }

  return {
    markdown,
    isReady,
    create,
    setContent,
    getMarkdown,
    destroy,
  }
}
