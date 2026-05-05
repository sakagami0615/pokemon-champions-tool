import type { LLMConfig } from '../../domain/entities/llm_config'

const BASE = '/api'

export async function getLLMConfig(): Promise<LLMConfig> {
  const res = await fetch(`${BASE}/llm-config`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function saveLLMConfig(config: LLMConfig): Promise<LLMConfig> {
  const res = await fetch(`${BASE}/llm-config`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getOllamaModels(baseUrl: string): Promise<string[]> {
  const res = await fetch(
    `${BASE}/ollama-models?base_url=${encodeURIComponent(baseUrl)}`
  )
  if (!res.ok) throw new Error(await res.text())
  const data = await res.json()
  return data.models as string[]
}
