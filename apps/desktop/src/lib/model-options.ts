import { getGlobalModelOptions, type HermesGateway, type ModelOptionsResponse } from '@/hermes'

interface ModelOptionsRequest {
  /** When true, restrict the list to routes configured in this profile. */
  explicitOnly?: boolean
  gateway?: HermesGateway
  /** Include setup rows for routes that are not authenticated yet. */
  includeUnconfigured?: boolean
  refresh?: boolean
  sessionId?: null | string
}

export function requestModelOptions({
  explicitOnly = false,
  gateway,
  includeUnconfigured = true,
  refresh = false,
  sessionId
}: ModelOptionsRequest): Promise<ModelOptionsResponse> {
  if (gateway) {
    const params: Record<string, unknown> = {}

    if (sessionId) {
      params.session_id = sessionId
    }

    if (refresh) {
      params.refresh = true
    }

    if (explicitOnly) {
      params.explicit_only = true
    }

    if (includeUnconfigured) {
      params.include_unconfigured = true
    }

    return gateway.request<ModelOptionsResponse>('model.options', params)
  }

  return getGlobalModelOptions({ explicitOnly, includeUnconfigured, ...(refresh ? { refresh: true } : {}) })
}
