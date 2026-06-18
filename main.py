import argparse
import csv
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


_QUOTING_MODES = {
    "minimal": csv.QUOTE_MINIMAL,
    "all": csv.QUOTE_ALL,
    "none": csv.QUOTE_NONE,
    "nonnumeric": csv.QUOTE_NONNUMERIC,
}

_QUOTING_DESCRIPTIONS = {
    csv.QUOTE_MINIMAL: "minimal (quotes only when necessary)",
    csv.QUOTE_ALL: "all fields are quoted",
    csv.QUOTE_NONE: "no quoting",
    csv.QUOTE_NONNUMERIC: "non-numeric fields are quoted",
}


def _resolve_quoting(mode: str) -> int:
    """Convert quoting mode string to csv module constant."""
    key = mode.strip().lower()
    if key in _QUOTING_MODES:
        return _QUOTING_MODES[key]
    valid = ", ".join(_QUOTING_MODES)
    raise ValueError(f"Unknown quoting mode '{mode}'. Valid: {valid}")


def _describe_quoting_mode(mode: int) -> str:
    return _QUOTING_DESCRIPTIONS.get(mode, "unknown quoting mode")


def detect_input_quoting(raw_bytes: bytes) -> str:
    encoding = _detect_encoding(raw_bytes)
    try:
        sample_text = raw_bytes.decode(encoding)
    except UnicodeDecodeError:
        sample_text = raw_bytes.decode(encoding, errors="replace")

    sample_text = _normalize_line_endings(sample_text)
    sample = "\n".join(sample_text.splitlines()[:20])
    if not sample.strip():
        return "入力ファイルが空です"

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=[",", "\t", ";", "|"])
        mode_desc = _describe_quoting_mode(dialect.quoting)
        return f"Detected quoting mode: {mode_desc}"
    except csv.Error:
        if '"' in sample:
            return "Quotes detected but quoting mode could not be determined"
        return "Quotes not detected in input"


def _explode_by_delimiter(df: pd.DataFrame, column: str, delimiter: str = "/") -> pd.DataFrame:
    """Split values in `column` by `delimiter` and create separate rows."""
    if column not in df.columns:
        return df
    df[column] = df[column].astype(str).str.split(delimiter)
    df = df.explode(column)
    df[column] = df[column].str.strip()
    return df.reset_index(drop=True)


def _normalize_line_endings(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def process_csv_bytes(raw_bytes: bytes, split_column: str | None = None, quoting: str = "minimal") -> str:
    encoding = _detect_encoding(raw_bytes)
    raw_text = raw_bytes.decode(encoding)
    raw_text = _normalize_line_endings(raw_text)
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
    df.to_csv(buf, index=False, encoding="utf-8", quoting=_resolve_quoting(quoting))
    return buf.getvalue()


def main():
    parser = argparse.ArgumentParser(description="CSV内の改行・文字コードを修正")
    parser.add_argument("input", nargs="?", default="input.csv", help="入力CSVファイル")
    parser.add_argument("--split-column", "-s", help="このカラムの `/` 区切り値を分割して行展開")
    parser.add_argument(
        "--quoting", "-q",
        default="minimal",
        choices=["minimal", "all", "none", "nonnumeric"],
        help="出力CSVの quoting モード（default: minimal）",
    )
    args = parser.parse_args()

    input_path = args.input
    stem = os.path.splitext(input_path)[0]
    output_path = f"{stem}_beautify.csv"

    with open(input_path, "rb") as f:
        raw_bytes = f.read()
    quoting_status = detect_input_quoting(raw_bytes)
    result = process_csv_bytes(raw_bytes, split_column=args.split_column, quoting=args.quoting)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)
    print(f"✅ {output_path} に出力しました")
    print(f"ℹ️ {quoting_status}")


if __name__ == "__main__":
    main()
