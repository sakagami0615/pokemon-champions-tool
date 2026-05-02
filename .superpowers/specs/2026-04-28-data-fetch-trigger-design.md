# データ取得トリガー機能 設計仕様書

## 概要

フロントエンドにデータ管理ページを新設し、GameWithのスクレイピングを起動するトリガーUIを追加する。
スクレイピングは非同期（バックグラウンド）で実行され、UIをブロックしない。
取得済みデータは日付ごとに管理され、ユーザーが使用するデータの日付を選択できる。

---

## 要件

- データ管理ページ（「データ管理」タブ）を新規作成する
- 「データ取得」ボタン押下で `POST /api/data/fetch` を呼び出す
- データ取得はバックグラウンド処理のため、ボタン押下後もUIは操作可能
- スクレイピング中の（当日取得中の）データは予測機能で使用できない
- 過去に取得済みのデータは引き続き予測機能で使用可能
- 利用可能な取得済み日付が複数ある場合、ユーザーがどの日付のデータを使用するか選択できる
- 選択した日付はバックエンドのインメモリで保持する（ブラウザ更新後も保持、Dockerコンテナ再起動でリセット）

---

## アーキテクチャ

### バックエンド変更

#### `IUsageRepository` インターフェース（`domain/repositories/usage_repository.py`）

追加メソッド：

```python
@abstractmethod
def get_available_dates(self) -> list[str]: ...

@abstractmethod
def get_usage_data_by_date(self, date: str) -> Optional[UsageData]: ...
```

#### `JsonUsageRepository`（`infrastructure/persistence/json_usage_repository.py`）

追加実装：

- `get_available_dates()`：`data/usage_rates/` 内の `YYYY-MM-DD.json` ファイルをスキャンし、日付文字列のリストを返す（降順ソート）
- `get_usage_data_by_date(date)`：指定日付のJSONファイルを読み込む

#### `data.py` ルーター（`presentation/routers/data.py`）

追加・変更：

- モジュールレベルのインメモリ状態：
  - `_scraping_in_progress: bool = False`
  - `_selected_date: str | None = None`
- `_do_fetch()` 更新：開始時に `_scraping_in_progress = True`、完了/失敗時に `False` へ戻す
- `GET /api/data/status` レスポンスを拡張：
  ```json
  {
    "pokemon_list_available": true,
    "usage_data_available": true,
    "usage_data_date": "2026-04-28T12:00:00",
    "scraping_in_progress": false,
    "selected_date": "2026-04-28",
    "available_dates": ["2026-04-28", "2026-04-27"]
  }
  ```
- `GET /api/data/pokemon/names`（変更）：`selected_date` が設定されている場合は該当日付の使用率データからポケモン名を返す。未設定の場合は従来通り `pokemon_list.json` から返す
- `GET /api/data/dates`（新規）：利用可能な日付一覧を返す
  ```json
  { "dates": ["2026-04-28", "2026-04-27"] }
  ```
- `POST /api/data/select-date`（新規）：使用する日付を設定する
  ```json
  // リクエスト
  { "date": "2026-04-27" }
  // レスポンス
  { "selected_date": "2026-04-27" }
  ```

#### 予測ルーター（`presentation/routers/prediction.py`）

- `selected_date` が設定されている場合は `get_usage_data_by_date(selected_date)` を使用
- `selected_date` が未設定の場合は `get_usage_data()`（最新）を使用
- スクレイピング中（`scraping_in_progress = True`）の間、現在進行中のスクレイピングは新しいファイルが保存されるまでデータを上書きしない。したがって `selected_date` が過去の日付であれば、スクレイピング中でも該当データはそのまま使用可能。スクレイピング完了後に新しい日付のファイルが追加されるため、予測機能への影響は完了後にのみ生じる。

### フロントエンド変更

#### `App.tsx`

- `Page` 型に `'data'` を追加：`type Page = 'prediction' | 'party' | 'data'`

#### `Header.tsx`

- ナビゲーションに「データ管理」タブを追加

#### `useDataManagement.ts`（新規：`application/hooks/`）

状態：

```typescript
interface DataManagementState {
  status: DataStatus | null
  isFetching: boolean
  fetchMessage: string | null
  error: string | null
}

interface DataStatus {
  pokemonListAvailable: boolean
  usageDataAvailable: boolean
  usageDataDate: string | null
  scrapingInProgress: boolean
  selectedDate: string | null
  availableDates: string[]
}
```

機能：

- マウント時に `GET /api/data/status` を呼び出してデータ状態を取得
- `scrapingInProgress` が `true` の間は3秒間隔でポーリング
- `triggerFetch()`：`POST /api/data/fetch` を呼び出す。レスポンス受信後すぐにボタンを有効化（ノンブロッキング）
- `selectDate(date: string)`：`POST /api/data/select-date` を呼び出し、状態を更新

#### `DataPage.tsx`（新規：`presentation/pages/`）

表示内容：

1. **データ取得状況セクション**
   - ポケモン一覧データの有無
   - 使用率データの有無と最終取得日時
   - スクレイピング中の場合はインジケーターを表示

2. **データ取得ボタン**
   - APIコール中（数百ms）はローディング表示・無効化
   - レスポンス受信後は有効化し「取得を開始しました」メッセージを表示
   - スクレイピング中はポーリングで状態を更新

3. **使用データ選択セクション**
   - 利用可能な日付をドロップダウンで表示
   - 選択変更時に `POST /api/data/select-date` を呼び出す
   - 取得済みデータがない場合は非表示

#### `usePokemonData.ts`（変更：`application/hooks/`）

- マウント時に `GET /api/data/status` を呼び出し `selected_date` と `available_dates` を確認する
- `selected_date` が設定されている場合：バックエンドはその日付のデータを使用して予測を実行するため、フロントエンド側は変更不要（予測APIが内部で正しい日付のデータを参照する）
- 既存の `GET /api/data/pokemon/names` はバックエンドの `selected_date` に基づいたポケモン名を返すよう、バックエンド側で対応する

---

## データフロー

```
[DataPage] ─ ボタン押下 → POST /api/data/fetch
                              ↓ レスポンス: {"status": "started"}
           ← ボタン有効化・「取得を開始しました」表示
           ← ポーリング(3秒) → GET /api/data/status
                                ↓ scraping_in_progress: true/false

[DataPage] ─ 日付選択 → POST /api/data/select-date
           ← selected_date 更新

[PredictionPage] → uses selected_date or latest → prediction
```

---

## エラーハンドリング

- `POST /api/data/fetch` 失敗時：エラーメッセージを DataPage に表示
- `POST /api/data/select-date` 失敗時：エラーメッセージを表示し選択を元に戻す
- ポーリング失敗時：静かに無視（次のポーリングで再試行）

---

## テスト方針

- バックエンド：
  - `get_available_dates()` のユニットテスト（ファイル存在/不在ケース）
  - `get_usage_data_by_date()` のユニットテスト
  - `_do_fetch()` でのフラグ更新のユニットテスト
  - `GET /api/data/status`、`GET /api/data/dates`、`POST /api/data/select-date` の統合テスト
- フロントエンド：
  - `useDataManagement` フックのユニットテスト（fetch mock使用）

---

## 対象外（スコープ外）

- GameWithスクレイピングの実際のHTML解析・セレクタ実装（別タスク）
- 選択日付のファイル永続化（Dockerコンテナ再起動でのリセットは許容）
- リアルタイムのスクレイピング進捗表示（完了/未完了のみ）
