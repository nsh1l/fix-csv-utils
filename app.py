import os

import streamlit as st

from main import process_csv_bytes

st.title("CSV 改行・文字コード変換")
st.write("入力ファイルの改行（フィールド内の改行）を空白に置換し、文字コードを自動判別して UTF-8 に変換します。")

uploaded_file = st.file_uploader("CSV ファイルを選択", type="csv")
split_column = st.text_input(
    "展開するカラム名（`/` 区切りの値を複数行に分割、未指定なら通常変換のみ）",
    placeholder="例: 品番",
)

if uploaded_file is not None:
    raw_bytes = uploaded_file.read()
    col = split_column.strip() if split_column.strip() else None
    with st.spinner("処理中..."):
        result = process_csv_bytes(raw_bytes, split_column=col)

    st.success("変換完了")
    base = os.path.splitext(uploaded_file.name)[0]
    st.download_button(
        label="変換後 CSV をダウンロード",
        data=result.encode("utf-8"),
        file_name=f"{base}_beautify.csv",
        mime="text/csv",
    )

    st.divider()
    st.subheader("プレビュー（先頭5行）")
    lines = result.splitlines()
    preview = "\n".join(lines[:6])
    st.text(preview)
