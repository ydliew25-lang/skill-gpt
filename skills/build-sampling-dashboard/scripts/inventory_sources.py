#!/usr/bin/env python3
"""清点门店交付文件。输出 JSON 元数据；工作表行数包含表头和说明行。"""

import argparse
import hashlib
import json
from pathlib import Path
import sys

SOURCE_EXTENSIONS = {".xlsx", ".md", ".markdown", ".txt", ".csv", ".tsv", ".pdf", ".json", ".jsonl"}


def file_metadata(path):
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            size += len(block)
            digest.update(block)
    return {"path": str(path), "size_bytes": size, "sha256": digest.hexdigest()}


def sheet_inventory(path):
    from openpyxl import load_workbook

    book = load_workbook(path, read_only=True, data_only=False, keep_links=False)
    try:
        sheets = []
        for sheet in book.worksheets:
            # 文件声明的范围可能含纯样式行，也可能只覆盖部分实际内容。
            sheet.reset_dimensions()
            count = sum(
                1 for row in sheet.iter_rows(values_only=True)
                if any(value is not None and (not isinstance(value, str) or value.strip()) for value in row)
            )
            sheets.append({"name": sheet.title, "nonempty_rows": count})
        return sheets
    finally:
        book.close()


def source_paths(paths):
    for path in paths:
        if path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_file() and child.suffix.lower() in SOURCE_EXTENSIONS and not child.name.startswith("~$"):
                    yield child
        else:
            yield path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="一个或多个文件或目录；指定目录时递归清点常见来源文件")
    args = parser.parse_args()
    files, errors, seen = [], [], set()
    for path in source_paths(args.paths):
        identity = path.resolve()
        if identity in seen:
            continue
        seen.add(identity)
        try:
            item = file_metadata(path)
        except OSError as exc:
            errors.append({"path": str(path), "error": type(exc).__name__})
            continue
        files.append(item)
        if path.suffix.lower() == ".xlsx":
            try:
                item["sheets"] = sheet_inventory(path)
            except ImportError:
                errors.append({"path": str(path), "error": "读取 XLSX 需在此 Python 环境安装 openpyxl 后重试"})
            except Exception as exc:
                # 上游解析异常有时包含具体的单元格值，只输出异常类型。
                errors.append({"path": str(path), "error": "无法读取工作簿 (" + type(exc).__name__ + ")"})
    print(json.dumps({"files": files, "errors": errors}, ensure_ascii=False, indent=2))
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
