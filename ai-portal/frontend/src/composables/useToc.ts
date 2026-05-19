import { computed } from 'vue'

export interface TocItem {
  id: string
  text: string
  level: number
  children?: TocItem[]
}

export function useToc(content: () => string) {
  const toc = computed(() => {
    const html = content()
    if (!html) return []

    const headings: TocItem[] = []
    const regex = /<h([1-4])[^>]*id=["']([^"']*)["'][^>]*>(.*?)<\/h\1>/gi
    let match

    while ((match = regex.exec(html)) !== null) {
      const level = parseInt(match[1])
      const id = match[2]
      const text = match[3].replace(/<[^>]*>/g, '').trim()
      if (id && text) {
        headings.push({ id, text, level })
      }
    }

    if (headings.length === 0) {
      const plainRegex = /^(#{1,4})\s+(.+)$/gm
      let plainMatch
      while ((plainMatch = plainRegex.exec(content())) !== null) {
        const level = plainMatch[1].length
        const text = plainMatch[2].trim()
        const id = text.toLowerCase().replace(/[^\w\u4e00-\u9fff]+/g, '-').replace(/^-|-$/g, '')
        headings.push({ id, text, level })
      }
    }

    return buildTree(headings)
  })

  function buildTree(items: TocItem[]): TocItem[] {
    const root: TocItem[] = []
    const stack: TocItem[] = []

    for (const item of items) {
      while (stack.length > 0 && stack[stack.length - 1].level >= item.level) {
        stack.pop()
      }

      if (stack.length === 0) {
        root.push(item)
      } else {
        const parent = stack[stack.length - 1]
        if (!parent.children) parent.children = []
        parent.children.push(item)
      }
      stack.push(item)
    }

    return root
  }

  return { toc }
}
