import { describe, expect, it } from 'vitest'

import type { SessionInfo } from '@/types/hermes'

import { rememberedSessionHasEnded } from './use-desktop-integrations'

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

describe('rememberedSessionHasEnded', () => {
  it('blocks cold-start restoration of an explicitly ended session', () => {
    expect(rememberedSessionHasEnded('ended', [session('ended', 123)])).toBe(true)
  })

  it('allows a live remembered session to restore', () => {
    expect(rememberedSessionHasEnded('live', [session('live', null)])).toBe(false)
  })

  it('matches a remembered compression-lineage root', () => {
    expect(rememberedSessionHasEnded('root', [session('tip', 456, 'root')])).toBe(true)
  })

  it('does not block an unloaded or unknown remembered session', () => {
    expect(rememberedSessionHasEnded('older-than-page', [session('recent', null)])).toBe(false)
  })
})
