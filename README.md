# fix-newline-in-csv

CSV のフィールド内に埋め込まれた改行を除去し、文字エンコーディングを自動判別して UTF-8 に変換するツールです。

## 機能

- **改行の除去** — フィールド内の `\r\n` / `\r` / `\n` を空白に置換
- **文字コード自動判別** — `chardet` で入力ファイルのエンコーディングを検出
- **HTML エンティティのデコード** — `依頼者名` 列の `&#xxxx;` を実際の文字に変換
- **継続行の結合** — 引用符なしで改行された行を自動的にマージ
- **不正行のスキップ** — 列数不一致の行は警告付きでスキップ

## 使い方

### CLI

```bash
uv run python main.py
```

`input.csv` を読み込み、`output.csv` に書き出します。

### Web UI (Streamlit)

```bash
uv run streamlit run app.py
```

ブラウザが開き、ファイルをアップロードして変換結果をダウンロードできます。

## インストール

```bash
uv sync
```

Python 3.12+ / uv が必要です。

## 構成

| ファイル | 説明 |
|---|---|
| `main.py` | コア処理 (`process_csv_bytes()`) と CLI エントリポイント |
| `app.py` | Streamlit Web UI |
| `pyproject.toml` | プロジェクト設定・依存関係 |
