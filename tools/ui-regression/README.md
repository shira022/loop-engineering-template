# @loop/ui-regression

ルートを総なめし、**console エラー / 未処理例外 / 失敗リクエスト / HTTP エラー / DOM・a11y 基本検査 /
レイアウト崩れ / スクリーンショット差分**を機械判定する CLI ハーネスです。

Playwright のテストランナー（`@playwright/test`）は使わず、素の Node スクリプトから
`playwright` ライブラリを直接操作します。

## 必要環境

- Node.js 20 以上（`node --test` を使用）
- Python 3（同梱の検証用サイトを配信する場合のみ）

## セットアップ

```bash
cd tools/ui-regression
npm install
npx playwright install chromium
# Linux で共有ライブラリ（libnspr4 など）が不足する場合:
# sudo npx playwright install-deps chromium
```

初回の `npm install` で `package-lock.json` が生成されます。
Chromium が既にキャッシュ済みなら `npx playwright install chromium` は何もしません。

## 使い方

```bash
# リポジトリルートから
node tools/ui-regression/sweep.mjs \
  --config tools/ui-regression/sweep.example.json \
  --out tools/ui-regression/out/run-manual
```

| オプション | 説明 |
|---|---|
| `--config <file>` | 設定 JSON（必須） |
| `--out <dir>` | 出力先。既定は `tools/ui-regression/out/run-<UTCyyyymmdd-HHMMSS>/` |
| `--update-baseline` | スクショを `baselineDir` にコピーし、差分判定をスキップ |
| `--no-screenshots` | スクショ撮影とピクセル差分を行わない |
| `--json` | レポート JSON を stdout に出力 |
| `--help` | ヘルプ |

終了コード:

| code | 意味 |
|---|---|
| `0` | 全ルート合格 |
| `1` | 違反あり、またはピクセル差分が閾値超過 |
| `2` | 設定エラー、設定ファイル読み込み失敗、ブラウザ起動失敗など |

### 設定例

`tools/ui-regression/sweep.example.json`:

```json
{
  "baseUrl": "http://127.0.0.1:8765",
  "viewport": { "width": 1280, "height": 800 },
  "routes": [
    { "name": "home", "path": "/index.html" },
    { "name": "clean", "path": "/clean.html", "waitFor": "#ready" },
    { "name": "broken", "path": "/broken.html" }
  ],
  "thresholds": {
    "maxConsoleErrors": 0,
    "maxPageErrors": 0,
    "maxFailedRequests": 0,
    "maxHttpErrors": 0,
    "maxA11yViolations": 0,
    "maxLayoutOverflowPx": 0,
    "pixelDiffRatio": 0.002
  },
  "a11y": true,
  "screenshots": true,
  "baselineDir": "tools/ui-regression/baseline"
}
```

- `baseUrl` / `baselineDir` / `--out` の相対パスは **実行時のカレントディレクトリ** 基準です。
- `waitFor` を指定すると、その CSS セレクタが出現するまで待ちます。
- `a11y` は DOM ヒューリスティック検査の有効/無効、`screenshots` は撮影の有効/無効です
  （`--no-screenshots` が指定された場合は撮影しません）。

## 出力

```
out/run-<timestamp>/
├── report.json
├── report.md
├── screens/<route>.png
└── diff/<route>.png        # ベースラインが存在する場合のみ
```

`report.json` はルートごとの `console_errors` / `page_errors` / `failed_requests` /
`http_errors` / `a11y` / `overflow_px` / `screenshot` / `diff_ratio` と、
`summary`（ルート数・合格数・失敗数・違反数）を含みます。

## 検査項目（ルートごと）

1. **console** — `console` イベントの `type === "error"`（先頭 5 件）
2. **pageerror** — 未処理例外
3. **requestfailed** — リクエスト失敗（URL と failure テキスト）
4. **http** — `response.status() >= 400`
5. **a11y** — axe を使わない DOM ヒューリスティック:
   - `html[lang]` が無い / 空
   - `img:not([alt])`（`alt=""` は装飾扱いで許容）
   - `button` にテキスト / `aria-label` / `aria-labelledby` / `title` が無い
   - `input:not([type=hidden])` に label / `aria-label` / `aria-labelledby` / `placeholder` が無い
   - `a` にテキスト / `aria-label` が無い
   - `h1` が 0 個または 2 個以上
   - 重複 `id`
6. **layout** — `documentElement.scrollWidth - clientWidth` が `maxLayoutOverflowPx` を超える
7. **pixel diff** — ベースライン PNG があり、`pixelmatch` の差分比率が `pixelDiffRatio` を超える

## ハーネス自身の動作確認手順

同梱の静的サイトには、違反ゼロの `clean.html` と、意図的に違反を入れた `broken.html` があります。

```bash
# 1. 検証用サイトを配信（リポジトリルートで実行）
python3 -m http.server 8765 --directory tools/ui-regression/testdata/site &

# 2. 違反検出の確認: broken が fail、clean が pass、終了コード 1
node tools/ui-regression/sweep.mjs \
  --config tools/ui-regression/sweep.example.json \
  --out tools/ui-regression/out/selftest
echo "exit=$?"   # => 1

# 3. ベースライン生成（このとき差分判定はスキップ）
node tools/ui-regression/sweep.mjs \
  --config tools/ui-regression/sweep.example.json \
  --update-baseline

# 4. 同一画面なので差分が出ないこと（diff_ratio ≈ 0、終了コード 1 は broken の違反分）
node tools/ui-regression/sweep.mjs \
  --config tools/ui-regression/sweep.example.json \
  --out tools/ui-regression/out/selftest2
node -e "const r=require('./tools/ui-regression/out/selftest2/report.json'); console.log(r.routes.map(x=>[x.name,x.diff_ratio]))"

# 5. 後片付け（baseline は残す）
rm -rf tools/ui-regression/out
kill %1
```

`broken.html` には以下が含まれています:
`html[lang]` 無し / `alt` 無し画像 / アクセシブル名の無いボタン / ラベルの無い input /
重複 id / `h1` 2 個 / 横スクロール / 404 画像 / 接続失敗リクエスト / `console.error` / 未処理例外。

## テスト

```bash
cd tools/ui-regression
npm test
```

レポート生成・閾値判定・ルート名のサニタイズなどのユニットテストを実行します。

## 注意

- `node_modules/` と `out/` は `tools/ui-regression/.gitignore` で無視されます。
- ベースラインは `tools/ui-regression/baseline/` に保存され、通常はリポジトリにコミットします。
- ハーネスは外部サイトへアクセスしません。検証は `127.0.0.1` のローカルサーバーに対して行います。
