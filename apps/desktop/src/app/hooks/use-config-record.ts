import { useStore } from '@nanostores/react'
import { useQuery } from '@tanstack/react-query'

import { getHermesConfigRecord } from '@/hermes'
import { queryClient } from '@/lib/query-client'
import { $activeGatewayProfile, normalizeProfileKey } from '@/store/profile'
import type { HermesConfigRecord } from '@/types/hermes'

// One profile-keyed cache for the whole config record (`GET /api/config`).
// Every settings surface (MCP, model, config) for that profile reads and writes
// through the same key, while a profile switch can never reuse the prior
// profile's record or accept a late response into the new profile's cache.
//
// Distinct from session/hooks/use-hermes-config.ts, which is side-effecting —
// it pushes personality/cwd/voice/… into the session stores for live chat.
export const HERMES_CONFIG_KEY = ['hermes-config-record'] as const

export const hermesConfigKey = (profile: string) => [...HERMES_CONFIG_KEY, normalizeProfileKey(profile)] as const

// staleTime 0 → serve cache instantly, background-revalidate on every mount.
export const useHermesConfigRecord = () => {
  const profile = useStore($activeGatewayProfile)

  return useQuery({ queryKey: hermesConfigKey(profile), queryFn: getHermesConfigRecord, staleTime: 0 })
}

export const setHermesConfigCache = (
  next: HermesConfigRecord | undefined | ((prev: HermesConfigRecord | undefined) => HermesConfigRecord | undefined)
): void => {
  const key = hermesConfigKey($activeGatewayProfile.get())

  void queryClient.setQueryData<HermesConfigRecord>(key, next)
}

export const invalidateHermesConfig = () => queryClient.invalidateQueries({ queryKey: HERMES_CONFIG_KEY })
