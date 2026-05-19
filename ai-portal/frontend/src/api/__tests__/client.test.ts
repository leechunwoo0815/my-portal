import { describe, it, expect } from 'vitest'
import api from '../client'

describe('API client', () => {
  it('has correct base URL', () => {
    expect(api.defaults.baseURL).toBeDefined()
  })

  it('has timeout configured', () => {
    expect(api.defaults.timeout).toBe(30000)
  })

  it('is axios instance', () => {
    expect(api.defaults).toBeDefined()
    expect(api.interceptors).toBeDefined()
    expect(typeof api.get).toBe('function')
    expect(typeof api.post).toBe('function')
    expect(typeof api.put).toBe('function')
    expect(typeof api.delete).toBe('function')
  })
})
