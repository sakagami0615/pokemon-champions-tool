# UX改善設計書：進捗表示・プロンプト管理・通知UI

## 概要

以下の3つの機能改善を実施する。

1. データ取得時の進捗状況表示（プログレスバー）
2. システムプロンプト・ユーザープロンプトの設定ファイル管理
3. 完了通知UIの変更（トースト導入）

---

## 機能1：データ取得進捗表示

### 要件

- データ取得中にプログレスバーを表示する
- 進捗はスクレイパーの実処理に基づいた真の進捗を反映する
- ページをリロードしても現在の進捗が表示される

### バックエンド設計

#### scraping_state.py の変更

```python
scraping_in_progress: bool = False
scraping_progress: int = 0    # 追加：0〜100
scraping_step: str = ""       # 追加：現在のステップ名
last_scraped_at: str | None = None  # 追加：最終取得完了日時（ISO形式）
selected_date: str | None = None
```

#### 進捗コールバックの伝搬

`data.py` の `_do_fetch()` からコールバックを各レイヤーに渡す。

```
data.py (_do_fetch)
  └─ ScrapePokemonListUseCase.execute(on_progress)
       └─ PokemonListScraper.fetch_pokemon_list(on_progress)
            └─ _fetch_all(grouped, on_progress, progress_start, progress_end)
```

`_fetch_all()` はポケモン1体取得完了ごとにコールバックを呼び出す。

#### 進捗の割り当て

| タイミング | progress | step |
|---|---|---|
| スクレイピング開始 | 0% | "ポケモン一覧ページを取得中..." |
| 通常ポケモン i/N 完了 | 5〜45% | "通常ポケモン取得中... (i/N)" |
| メガポケモン i/M 完了 | 45〜50% | "メガポケモン取得中... (i/M)" |
| 使用率データ取得開始 | 50% | "使用率データ取得中..." |
| 全完了 | 100% | "" |

- 使用率データ取得（`GameWithScraper.fetch_usage_ranking()`）は現状1リクエストで完了するため、50%→100%は即時遷移する。将来の使用率スクレイピング拡充時に粒度を追加する。

#### APIレスポンス変更

`GET /api/data/status` のレスポンスに以下を追加する。

```json
{
  "scraping_in_progress": false,
  "scraping_progress": 100,
  "scraping_step": "",
  "last_scraped_at": "2026-05-07T14:32:00",
  ...
}
```

### フロントエンド設計

#### DataStatus 型の変更

```typescript
interface DataStatus {
  scraping_in_progress: boolean
  scraping_progress: number      // 追加
  scraping_step: string          // 追加
  last_scraped_at: string | null // 追加
  ...
}
```

#### SettingsPage.tsx の変更

- "スクレイピング実行中..." テキストを削除
- プログレスバーコンポーネントを追加（`scraping_in_progress: true` のとき表示）

表示例：
```
通常ポケモン取得中... (87/203)
[■■■■■■■■■□□□□□□□□□□□] 42%
```

#### リロード時の動作

- バックエンドにプログレス状態が保持されるため、リロード後も現在の進捗がそのまま表示される
- ポーリング（3秒間隔）が自動で再開する

---

## 機能2：プロンプト設定ファイル管理

### 要件

- システムプロンプトとユーザープロンプトテンプレートを設定ファイルで管理する
- サーバー再起動なしでファイル変更が即時反映される
- `predict_use_case.py` のハードコードを廃止する

### ファイル構成

新規ファイル `backend/config/prompts.yaml` を作成する。

```yaml
system_prompt: |
  あなたはポケモンチャンピオンズの対戦分析AIです。
  与えられた情報をもとに、相手プレイヤーが選出しそうなポケモン3体のパターンを3つ予想してください。

  回答は必ず以下の形式で出力してください：
  パターン1: ポケモン名A, ポケモン名B, ポケモン名C
  パターン2: ポケモン名D, ポケモン名E, ポケモン名F
  パターン3: ポケモン名G, ポケモン名H, ポケモン名I

  可能性が高い順に並べてください。確率の数値は不要です。

user_prompt_template: |
  【相手パーティ（6体）】
  {opponent_party}

  【自分のパーティ（6体）】
  {my_party}

  【相手パーティの使用率データ】
  {usage_text}

  シングルバトル3体選出です。相手が選出しそうな3体のパターンを3つ予想してください。
```

### バックエンド構成

#### ドメイン層

- `domain/entities/prompt_config.py`：`PromptConfig` データクラス（`system_prompt: str`、`user_prompt_template: str`）
- `domain/repositories/prompt_config_repository.py`：`IPromptConfigRepository` インターフェース（`get_prompt_config() -> PromptConfig`）

#### インフラ層

- `infrastructure/persistence/yaml_prompt_config_repository.py`：YAMLファイルを読み込む実装
  - `predict()` 呼び出しのたびにファイルを読み込む（再起動不要で即時反映）

#### アプリケーション層

- `PredictUseCase` のコンストラクタに `IPromptConfigRepository` を追加
- `predict()` 内で `SYSTEM_PROMPT` ハードコード定数を削除し、リポジトリから取得したプロンプトを使用

---

## 機能3：完了通知UIの変更

### 要件

- データ取得完了時にトースト（ポップアップ）で通知する
- リロード後も完了通知が表示される

### 実装方針

#### トーストライブラリの導入

`sonner` を `frontend` に追加する。`App.tsx` に `<Toaster position="top-right" />` を追加。

#### リロード対応

バックエンドの `last_scraped_at` を活用する。

- スクレイピング完了時に `last_scraped_at` を記録
- フロントエンドは `useDataManagement` の初回 `loadStatus()` で `last_scraped_at` を取得
- フロントエンドは `localStorage` に `last_notified_at` を保存
- `last_scraped_at > last_notified_at`（または `last_notified_at` が未設定）の場合、トーストを表示して `last_notified_at` を更新

この方式によりリロード後でも未通知の完了イベントを検知できる。

---

## 変更ファイル一覧

### バックエンド

| ファイル | 変更種別 |
|---|---|
| `src/application/state/scraping_state.py` | 変更：フィールド追加 |
| `src/application/use_cases/scrape_pokemon_list_use_case.py` | 変更：コールバック引数追加 |
| `src/application/use_cases/predict_use_case.py` | 変更：PromptConfigRepository DI、ハードコード削除 |
| `src/domain/entities/prompt_config.py` | 新規 |
| `src/domain/repositories/prompt_config_repository.py` | 新規 |
| `src/infrastructure/external/pokemon_list_scraper.py` | 変更：コールバック引数追加 |
| `src/infrastructure/persistence/yaml_prompt_config_repository.py` | 新規 |
| `src/presentation/routers/data.py` | 変更：進捗更新処理・last_scraped_at 記録追加 |
| `config/prompts.yaml` | 新規 |

### フロントエンド

| ファイル | 変更種別 |
|---|---|
| `src/infrastructure/api/dataApi.ts` | 変更：DataStatus 型に3フィールド追加 |
| `src/application/hooks/useDataManagement.ts` | 変更：トースト呼び出し追加 |
| `src/presentation/pages/SettingsPage.tsx` | 変更：プログレスバー追加 |
| `src/App.tsx` | 変更：Toaster コンポーネント追加 |
| `package.json` | 変更：sonner 追加 |
