export type Provider = 'anthropic' | 'openai' | 'google' | 'ollama'

export interface ProviderSettings {
  model: string | null
  base_url: string | null
  api_key: string | null
}

export interface LLMConfig {
  selected_provider: Provider
  providers: Record<Provider, ProviderSettings>
}

export const PROVIDER_LABELS: Record<Provider, string> = {
  anthropic: 'Anthropic',
  openai: 'OpenAI',
  google: 'Google',
  ollama: 'Ollama',
}

export const PROVIDER_MODELS: Record<Provider, string[]> = {
  anthropic: ['claude-opus-4-7', 'claude-sonnet-4-6', 'claude-haiku-4-5'],
  openai: ['gpt-4o', 'gpt-4o-mini', 'o1', 'o1-mini'],
  google: ['gemini-2.5-pro', 'gemini-2.0-flash', 'gemini-1.5-flash'],
  ollama: [],
}

export const PROVIDERS: Provider[] = ['anthropic', 'openai', 'google', 'ollama']
