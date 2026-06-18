import argparse
import html
import io
import os
import re

import chardet
import pandas as pd


def _detect_encoding(raw: bytes) -> str:
    result = chardet.detect(raw[:10000])
    return result["encoding"]


def _merge_continuation_lines(text: str) -> str:
    _DATA_LINE_PATTERN = re.compile(r"^[A-Za-z]{0,2}\d{8,}")
    lines = text.splitlines()
    merged = [lines[0]]
    for line in lines[1:]:
        if _DATA_LINE_PATTERN.match(line):
            merged.append(line)
        else:
            merged[-1] += line
    return "\n".join(merged)


def _explode_by_delimiter(df: pd.DataFrame, column: str, delimiter: str = "/") -> pd.DataFrame:
    """Split values in `column` by `delimiter` and create separate rows."""
    if column not in df.columns:
        return df
    df[column] = df[column].astype(str).str.split(delimiter)
    df = df.explode(column)
    df[column] = df[column].str.strip()
    return df.reset_index(drop=True)


def process_csv_bytes(raw_bytes: bytes, split_column: str | None = None) -> str:
    encoding = _detect_encoding(raw_bytes)
    raw_text = raw_bytes.decode(encoding)
    clean_text = _merge_continuation_lines(raw_text)
    df = pd.read_csv(io.StringIO(clean_text), encoding=encoding, on_bad_lines="warn")
    if "依頼者名" in df.columns:
        df["依頼者名"] = df["依頼者名"].apply(html.unescape)
    cols = ["comment", "description"]
    for c in cols:
        if c in df.columns:
            df[c] = df[c].astype(str).str.replace(r"\r\n|\r|\n", " ", regex=True)
    if split_column and split_column in df.columns:
        df = _explode_by_delimiter(df, split_column)
    buf = io.StringIO()
    df.to_csv(buf, index=False, encoding="utf-8")
    return buf.getvalue()


def main():
    parser = argparse.ArgumentParser(description="CSV内の改行・文字コードを修正")
    parser.add_argument("input", nargs="?", default="input.csv", help="入力CSVファイル")
    parser.add_argument("--split-column", "-s", help="このカラムの `/` 区切り値を分割して行展開")
    args = parser.parse_args()

    input_path = args.input
    stem = os.path.splitext(input_path)[0]
    output_path = f"{stem}_beautify.csv"

    with open(input_path, "rb") as f:
        raw_bytes = f.read()
    result = process_csv_bytes(raw_bytes, split_column=args.split_column)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)
    print(f"✅ {output_path} に出力しました")


if __name__ == "__main__":
    main()
