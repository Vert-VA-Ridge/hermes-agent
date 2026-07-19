import { describe, expect, it } from 'vitest'

import type { SessionInfo } from '@/types/hermes'

import { rememberedSessionShouldNotAutoRestore } from './use-desktop-integrations'

function session(id: string, endedAt: null | number, root: null | string = null): SessionInfo {
  return {
    _lineage_root_id: root,
    ended_at: endedAt,
    id,
    input_tokens: 0,
    is_active: endedAt == null,
    last_active: 1,
    message_count: 1,
    model: 'max',
    output_tokens: 0,
    preview: null,
    source: 'cli',
    started_at: 1,
    title: null,
    tool_call_count: 0
  }
}

describe('rememberedSessionShouldNotAutoRestore', () => {
  it('blocks cold-start restoration of an explicitly ended session', () => {
    expect(rememberedSessionShouldNotAutoRestore('ended', [session('ended', 123)])).toBe(true)
  })

  it('allows a live remembered session to restore', () => {
    expect(rememberedSessionShouldNotAutoRestore('live', [session('live', null)])).toBe(false)
  })

  it('matches a remembered compression-lineage root', () => {
    expect(rememberedSessionShouldNotAutoRestore('root', [session('tip', 456, 'root')])).toBe(true)
  })

  it('blocks an absent remembered session after refresh', () => {
    expect(rememberedSessionShouldNotAutoRestore('archived-or-unknown', [session('recent', null)])).toBe(true)
  })
})
