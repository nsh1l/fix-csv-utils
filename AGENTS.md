# AGENTS.md - Fix CSV Utils

## プロジェクト概要
CSV ファイルのクリーニング・変換ツール。Streamlit ベースの Web UI と CLI を提供。

## 技術スタック
- Python 3.13
- Streamlit
- uv（パッケージ管理）

## ビルド・実行コマンド
```bash
# 依存関係インストール
uv sync

# Streamlit アプリ起動
streamlit run app.py

# CLI 実行
python3 main.py input.csv output.csv
```

## ファイル構造
- `app.py` - Streamlit Web UI
- `main.py` - CLI エントリーポイント
- `.streamlit/` - Streamlit 設定
- `pyproject.toml` - プロジェクト設定

## コードスタイル
- ruff 使用（ruff.toml 参照）
- 行長：120 文字
- インデント：スペース 4 個