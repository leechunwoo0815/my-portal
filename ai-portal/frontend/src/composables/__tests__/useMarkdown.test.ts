import { describe, it, expect } from 'vitest'
import { useMarkdown } from '../useMarkdown'

describe('useMarkdown', () => {
  it('renders markdown to HTML', () => {
    const { renderMd } = useMarkdown()
    const html = renderMd('# Hello World')
    expect(html).toContain('<h1')
    expect(html).toContain('Hello World')
  })

  it('handles empty input', () => {
    const { renderMd } = useMarkdown()
    const html = renderMd('')
    expect(html).toBeDefined()
  })

  it('handles null input', () => {
    const { renderMd } = useMarkdown()
    const html = renderMd(null)
    expect(html).toBe('')
  })

  it('renders code blocks', () => {
    const { renderMd } = useMarkdown()
    const html = renderMd('```python\nprint("hello")\n```')
    expect(html).toContain('hello')
  })

  it('renders links', () => {
    const { renderMd } = useMarkdown()
    const html = renderMd('[Click](https://example.com)')
    expect(html).toContain('href')
    expect(html).toContain('example.com')
  })
})
