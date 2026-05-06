import { useState } from 'react'
import type { LLMConfig, Provider } from '../../domain/entities/llm_config'
import { PROVIDER_LABELS, PROVIDER_MODELS, PROVIDERS } from '../../domain/entities/llm_config'

interface Props {
  config: LLMConfig
  ollamaModels: string[]
  isSaving: boolean
  isFetchingModels: boolean
  error: string | null
  saveMessage: string | null
  isSelectedModelValid: boolean
  onSelectProvider: (p: Provider) => void
  onSelectModel: (p: Provider, model: string) => void
  onUpdateApiKey: (p: Provider, key: string) => void
  onUpdateOllamaBaseUrl: (url: string) => void
  onFetchOllamaModels: () => void
  onSave: () => void
}

export default function ModelSettings({
  config,
  ollamaModels,
  isSaving,
  isFetchingModels,
  error,
  saveMessage,
  isSelectedModelValid,
  onSelectProvider,
  onSelectModel,
  onUpdateApiKey,
  onUpdateOllamaBaseUrl,
  onFetchOllamaModels,
  onSave,
}: Props) {
  const [focusedApiKeyProvider, setFocusedApiKeyProvider] = useState<Provider | null>(null)

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">モデル設定</h2>

      <div className="space-y-3">
        {PROVIDERS.map((provider) => {
          const isSelected = config.selected_provider === provider
          const settings = config.providers[provider]
          const models =
            provider === 'ollama' ? ollamaModels : PROVIDER_MODELS[provider]

          return (
            <div
              key={provider}
              className={`border rounded-lg p-4 space-y-3 ${
                isSelected
                  ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20'
                  : 'border-gray-200 dark:border-gray-700'
              }`}
            >
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="provider"
                  value={provider}
                  checked={isSelected}
                  onChange={() => onSelectProvider(provider)}
                  className="accent-indigo-600"
                />
                <span className="font-medium">{PROVIDER_LABELS[provider]}</span>
              </label>

              {provider === 'ollama' ? (
                <div className="space-y-2 ml-6">
                  <div className="flex items-center gap-2">
                    <label className="text-sm text-gray-600 dark:text-gray-400 w-28">
                      エンドポイント
                    </label>
                    <input
                      type="text"
                      value={settings.base_url ?? ''}
                      onChange={(e) => onUpdateOllamaBaseUrl(e.target.value)}
                      placeholder="http://{IP address}:11434"
                      className="flex-1 px-2 py-1 text-sm border rounded dark:bg-gray-800 dark:border-gray-600"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <label className="text-sm text-gray-600 dark:text-gray-400 w-28">
                      モデル
                    </label>
                    <select
                      value={settings.model ?? ''}
                      onChange={(e) => onSelectModel(provider, e.target.value)}
                      disabled={ollamaModels.length === 0}
                      className="flex-1 px-2 py-1 text-sm border rounded dark:bg-gray-800 dark:border-gray-600 disabled:opacity-50"
                    >
                      {ollamaModels.length === 0 ? (
                        settings.model ? (
                          <option value={settings.model}>{settings.model}</option>
                        ) : (
                          <option value="">未取得</option>
                        )
                      ) : (
                        ollamaModels.map((m) => (
                          <option key={m} value={m}>
                            {m}
                          </option>
                        ))
                      )}
                    </select>
                    <button
                      onClick={onFetchOllamaModels}
                      disabled={isFetchingModels}
                      className="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-700 rounded hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50"
                    >
                      {isFetchingModels ? '取得中...' : '一覧を取得'}
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-2 ml-6">
                  <div className="flex items-center gap-2">
                    <label className="text-sm text-gray-600 dark:text-gray-400 w-28">
                      モデル
                    </label>
                    <select
                      value={settings.model ?? ''}
                      onChange={(e) => onSelectModel(provider, e.target.value)}
                      className="flex-1 px-2 py-1 text-sm border rounded dark:bg-gray-800 dark:border-gray-600"
                    >
                      {models.map((m) => (
                        <option key={m} value={m}>
                          {m}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="flex items-center gap-2">
                    <label className="text-sm text-gray-600 dark:text-gray-400 w-28">
                      APIキー
                    </label>
                    <input
                      type={focusedApiKeyProvider === provider ? 'text' : 'password'}
                      value={
                        focusedApiKeyProvider === provider
                          ? (settings.api_key ?? '')
                          : (settings.api_key ? '*'.repeat(10) : '')
                      }
                      onFocus={() => setFocusedApiKeyProvider(provider)}
                      onBlur={() => setFocusedApiKeyProvider(null)}
                      onChange={(e) => onUpdateApiKey(provider, e.target.value)}
                      placeholder="API Key here"
                      className="flex-1 px-2 py-1 text-sm border rounded dark:bg-gray-800 dark:border-gray-600"
                    />
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>

      {error && <p className="text-sm text-red-500">{error}</p>}
      {saveMessage && <p className="text-sm text-green-600">{saveMessage}</p>}

      <button
        onClick={onSave}
        disabled={isSaving || !isSelectedModelValid}
        className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-bold disabled:opacity-50"
      >
        {isSaving ? '保存中...' : '保存'}
      </button>
    </div>
  )
}
