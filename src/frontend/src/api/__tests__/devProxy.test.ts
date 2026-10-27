import configSource from '../../../vite.config.ts?raw'
import { devProxy } from '@/api/devProxy'

describe('dev proxy', () => {
  it('the dev server should proxy documents and chat to the api', () => {
    // Given

    // When

    // Then
    expect(configSource).toContain('proxy: devProxy')
    expect(devProxy['/documents']).toBe('http://127.0.0.1:8000')
    expect(devProxy['/chat']).toBe('http://127.0.0.1:8000')
  })
})
