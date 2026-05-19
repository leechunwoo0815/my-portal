import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'

const md = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true,
  highlight: (code: string, lang: string) => {
    let highlighted: string
    if (lang && hljs.getLanguage(lang)) {
      try {
        highlighted = hljs.highlight(code, { language: lang, ignoreIllegals: true }).value
      } catch { highlighted = md.utils.escapeHtml(code) }
    } else {
      highlighted = md.utils.escapeHtml(code)
    }
    return `<div class="code-block"><div class="code-block-header"><span class="code-block-lang">${lang || ''}</span><button class="code-block-copy" onclick="navigator.clipboard.writeText(this.closest('.code-block').querySelector('code').textContent).then(()=>{this.textContent='已复制';setTimeout(()=>{this.textContent='复制'},1500)})">复制</button></div><pre class="hljs"><code>${highlighted}</code></pre></div>`
  },
})

export function useMarkdown() {
  const renderMd = (content?: string | null) => (content ? md.render(content) : '')
  return { md, renderMd }
}
