import { useState, useEffect, useCallback } from 'react'
import type { LLMConfig, Provider } from '../../domain/entities/llm_config'
import { getLLMConfig, saveLLMConfig, getOllamaModels } from '../../infrastructure/api/llmConfigApi'

export function useLLMConfig() {
  const [config, setConfig] = useState<LLMConfig | null>(null)
  const [ollamaModels, setOllamaModels] = useState<string[]>([])
  const [isSaving, setIsSaving] = useState(false)
  const [isFetchingModels, setIsFetchingModels] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [saveMessage, setSaveMessage] = useState<string | null>(null)

  useEffect(() => {
    getLLMConfig()
      .then(setConfig)
      .catch((e: unknown) => setError(String(e)))
  }, [])

  const updateProvider = useCallback(
    (provider: Provider) => {
      if (!config) return
      setConfig({ ...config, selected_provider: provider })
    },
    [config]
  )

  const updateModel = useCallback(
    (provider: Provider, model: string) => {
      if (!config) return
      setConfig({
        ...config,
        providers: {
          ...config.providers,
          [provider]: { ...config.providers[provider], model },
        },
      })
    },
    [config]
  )

  const updateOllamaBaseUrl = useCallback(
    (url: string) => {
      if (!config) return
      setConfig({
        ...config,
        providers: {
          ...config.providers,
          ollama: { ...config.providers.ollama, base_url: url },
        },
      })
    },
    [config]
  )

  const fetchOllamaModels = useCallback(async () => {
    if (!config?.providers.ollama.base_url) return
    setIsFetchingModels(true)
    setError(null)
    try {
      const models = await getOllamaModels(config.providers.ollama.base_url)
      setOllamaModels(models)
    } catch {
      setError('Ollamaへの接続に失敗しました')
    } finally {
      setIsFetchingModels(false)
    }
  }, [config])

  const save = useCallback(async () => {
    if (!config) return
    setIsSaving(true)
    setError(null)
    try {
      await saveLLMConfig(config)
      setSaveMessage('保存しました')
      setTimeout(() => setSaveMessage(null), 3000)
    } catch {
      setError('保存に失敗しました')
    } finally {
      setIsSaving(false)
    }
  }, [config])

  const isSelectedModelValid =
    config !== null &&
    (config.providers[config.selected_provider]?.model ?? null) !== null

  return {
    config,
    ollamaModels,
    isSaving,
    isFetchingModels,
    error,
    saveMessage,
    isSelectedModelValid,
    updateProvider,
    updateModel,
    updateOllamaBaseUrl,
    fetchOllamaModels,
    save,
  }
}
