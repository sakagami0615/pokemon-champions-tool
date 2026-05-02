# フロントエンド Clean Architecture フォルダ再編 設計書

## 概要

フロントエンド (`frontend/src/`) のディレクトリ構成を、種類別（components/hooks/pages/api/types）から
Clean Architecture のレイヤー別（domain/infrastructure/presentation）に再編する。
ロジックの変更は行わず、ファイルの移動と import パスの更新のみを実施する。

## スコープ

- 対象: `frontend/src/` 配下のソースファイル
- 除外: `dist/`, `node_modules/`, 設定ファイル（vite.config.ts 等）

## 現在の構成

```
src/
  api/client.ts
  App.css
  App.tsx
  assets/react.svg
  components/
    DarkModeToggle.tsx
    Header.tsx
    PartyInput.tsx
    PatternCard.tsx
    PokemonCard.tsx
    PokemonSlot.tsx
    PredictionResult.tsx
  hooks/useDarkMode.ts
  index.css
  main.tsx
  pages/
    PartyPage.tsx
    PredictionPage.tsx
  types/index.ts
  vite-env.d.ts
```

## 目標の構成

```
src/
  domain/
    entities/
      index.ts
  infrastructure/
    api/
      client.ts
  presentation/
    components/
      DarkModeToggle.tsx
      Header.tsx
      PartyInput.tsx
      PatternCard.tsx
      PokemonCard.tsx
      PokemonSlot.tsx
      PredictionResult.tsx
    pages/
      PartyPage.tsx
      PredictionPage.tsx
    hooks/
      useDarkMode.ts
  assets/
    react.svg
  App.css
  App.tsx
  index.css
  main.tsx
  vite-env.d.ts
```

## レイヤー定義

### domain/entities/
ビジネスエンティティの型定義。フレームワーク・外部ライブラリへの依存なし。
- `RatedItem`, `EvSpread`, `UsageEntry`, `PredictionPattern`, `PredictionResult`, `Party`, `PartiesData`

### infrastructure/api/
バックエンド API との通信を担う。fetch を使った HTTP クライアント関数群。
- `recognize`, `predict`, `getParties`, `createParty`, `updateParty`, `deleteParty`, `setLastUsedParty`, `fetchData`, `getDataStatus`, `getPokemonNames`

### presentation/
React コンポーネント、ページ、UI フック。フレームワーク依存コードはここに集約。

- `components/`: 再利用可能な UI コンポーネント
- `pages/`: ルーティング単位のページコンポーネント
- `hooks/`: React カスタムフック

### src/ 直下（変更なし）
エントリーポイントとグローバルスタイルはレイヤーに属さないため src/ 直下に残す。
- `App.tsx`, `main.tsx`, `App.css`, `index.css`, `vite-env.d.ts`, `assets/`

## Import パス変更一覧

| ファイル | 変更前 import | 変更後 import |
|---|---|---|
| `presentation/components/PartyInput.tsx` | `../api/client` | `../../infrastructure/api/client` |
| `presentation/components/PatternCard.tsx` | `../types` | `../../domain/entities` |
| `presentation/components/PokemonCard.tsx` | `../types` | `../../domain/entities` |
| `presentation/components/PredictionResult.tsx` | `../types` | `../../domain/entities` |
| `presentation/pages/PartyPage.tsx` | `../api/client` | `../../infrastructure/api/client` |
| `presentation/pages/PartyPage.tsx` | `../types` | `../../domain/entities` |
| `presentation/pages/PredictionPage.tsx` | `../api/client` | `../../infrastructure/api/client` |
| `presentation/pages/PredictionPage.tsx` | `../types` | `../../domain/entities` |
| `App.tsx` | `./hooks/useDarkMode` | `./presentation/hooks/useDarkMode` |
| `App.tsx` | `./pages/PredictionPage` | `./presentation/pages/PredictionPage` |
| `App.tsx` | `./pages/PartyPage` | `./presentation/pages/PartyPage` |
| `App.tsx` | `./components/Header` | `./presentation/components/Header` |

## 今後の拡張余地

`application/` 層は今回作成しないが、将来的に UseCases を導入する場合は以下に追加する:
```
src/
  application/
    useCases/
```

## 制約

- ロジックの変更なし（型、関数シグネチャ、処理内容は一切変えない）
- `frontend/` 直下の設定ファイル（Dockerfile, eslint.config.js 等）は対象外
