export function formatDate(d: string | Date | undefined): string {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\//g, '-')
}

export function formatDateTime(d: string | Date | undefined): string {
  if (!d) return ''
  return new Date(d).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }).replace(/\//g, '-')
}

export function extractOptions(items: any[], field: string): string[] {
  const set = new Set<string>()
  items.forEach(item => {
    if (item[field]) {
      item[field].split(',').map((s: string) => s.trim()).filter(Boolean).forEach((s: string) => set.add(s))
    }
  })
  return Array.from(set).sort()
}
