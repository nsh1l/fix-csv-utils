import io
import os

import pandas as pd
import streamlit as st

from main import detect_input_quoting, process_csv_bytes

st.title("CSV 改行・文字コード変換")
st.write("入力ファイルの改行（フィールド内の改行）を空白に置換し、文字コードを自動判別して UTF-8 に変換します。")

uploaded_file = st.file_uploader("CSV ファイルを選択", type="csv")
split_column = st.text_input(
    "展開するカラム名（`/` 区切りの値を複数行に分割、未指定なら通常変換のみ）",
    placeholder="例: 品番",
)
quoting = st.selectbox(
    "出力のダブルクオートモード",
    options=["minimal", "all", "none", "nonnumeric"],
    index=0,
    help=(
        "minimal: 必要最小限のみ（デフォルト）\n"
        "all: すべてのフィールドをクオート\n"
        "none: 一切クオートしない\n"
        "nonnumeric: 数字以外をクオート"
    ),
)

if uploaded_file is not None:
    raw_bytes = uploaded_file.read()
    col = split_column.strip() if split_column.strip() else None
    with st.spinner("処理中..."):
        result = process_csv_bytes(raw_bytes, split_column=col, quoting=quoting)
    status = detect_input_quoting(raw_bytes)

    st.success("変換完了")
    st.info(status)
    base = os.path.splitext(uploaded_file.name)[0]

    st.download_button(
        label="変換後 CSV をダウンロード",
        data=result.encode("utf-8"),
        file_name=f"{base}_beautify.csv",
        mime="text/csv",
    )

    st.divider()
    st.subheader("プレビュー（先頭5行）")
    try:
        preview_df = pd.read_csv(io.StringIO(result))
        st.dataframe(preview_df.head(5))
    except pd.errors.EmptyDataError:
        st.info("CSVに有効な行が含まれていません")
