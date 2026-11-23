#!/usr/bin/env python3
"""Create a sampling annotation workbook or check its local evidence links."""
import argparse
import re
import sys
from io import BytesIO
from pathlib import Path
from zipfile import BadZipFile

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.utils.exceptions import InvalidFileException


SOURCE = "逐条原文"
TAGS = "标签明细"
HEADERS = {
    SOURCE: "批次 会话 原文ID 原始位置 来源 发言人 完整原文 处理说明".split(),
    TAGS: ("标签ID 批次 会话 归属主体 商品角色及对象 场景 字段代码 细项 业务值 Q02值状态 "
           "Q01记录依据 表达方式 主证据ID 旁证ID 判断理由 规则版本 Q04状态").split(),
}
ENUMS = {
    "Q02值状态": set("已记录 未提及 拒答 无法识别 未接通 待回传 未观察到 不适用".split()),
    "Q01记录依据": set("顾客明示 客观行为 系统推断 外部回传 人工复核".split()),
    "Q04状态": set("有效 已被更正 待确认".split()),
    "表达方式": {"", "明示", "语境推定", "分析假设"},
}
DEFAULT_SCHEMA = Path(__file__).resolve().parents[1] / "references" / "schema-v0.2.md"


def as_text(value):
    return "" if value is None else str(value).strip()


def create(path):
    book = Workbook()
    book.remove(book.active)
    for title, headers in HEADERS.items():
        sheet = book.create_sheet(title)
        sheet.append(headers)
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions
        for cell in sheet[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="28575C")
            width = 60 if cell.value in {"完整原文", "处理说明", "判断理由"} else 20
            sheet.column_dimensions[get_column_letter(cell.column)].width = width
    buffer = BytesIO()
    book.save(buffer)
    with path.open("xb") as output:
        output.write(buffer.getvalue())


def field_codes(path):
    codes = set()
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        cells = line.strip().strip("|").split("|")
        if len(cells) != 6:
            continue
        match = re.fullmatch(r"([A-Z]+\d+)\s+.+", cells[4].strip())
        if match:
            codes.add(match.group(1))
    if not codes:
        raise ValueError("字典中没有识别到六列字段表（第五列为“代码 名称”）")
    return codes


def records(book, title):
    if title not in book.sheetnames:
        raise ValueError(f"缺少工作表“{title}”")
    sheet = book[title]
    sheet.reset_dimensions()  # Imported workbooks can have stale worksheet dimensions.
    rows = sheet.values
    header = [as_text(cell) for cell in next(rows, ())]
    for name in HEADERS[title]:
        if header.count(name) != 1:
            raise ValueError(f"{title} 首行必须有且仅有一列“{name}”")
    for number, values in enumerate(rows, 2):
        row = dict(zip(header, map(as_text, values)))
        row = {name: row.get(name, "") for name in HEADERS[title]}
        if any(row.values()):
            yield number, row


def need(row, fields, at, errors):
    missing = [field for field in fields if not row[field]]
    if missing:
        errors.append(f"{at} 缺少 {'、'.join(missing)}")


def check(book, codes):
    errors = []
    sources = {}
    for number, row in records(book, SOURCE):
        at = f"{SOURCE} 第{number}行"
        need(row, ["批次", "会话", "原文ID", "原始位置", "来源", "完整原文"], at, errors)
        key = (row["批次"], row["会话"], row["原文ID"])
        if key in sources:
            errors.append(f"{at} 原文ID在同批次同会话内重复")
        sources[key] = (at, row["处理说明"])
    if not sources:
        errors.append(f"{SOURCE} 缺少原文记录")

    covered = set()
    ids = set()
    count = 0
    for number, row in records(book, TAGS):
        count += 1
        at = f"{TAGS} 第{number}行"
        need(row, ["标签ID", "批次", "会话", "归属主体", "商品角色及对象", "场景",
                   "主证据ID", "规则版本"], at, errors)
        if row["标签ID"] in ids:
            errors.append(f"{at} 标签ID重复")
        ids.add(row["标签ID"])
        if row["字段代码"] not in codes:
            errors.append(f"{at} 字段代码未在字典中找到")
        for field, allowed in ENUMS.items():
            if row[field] not in allowed:
                errors.append(f"{at} {field}不符合 V0.2 枚举")
        status = row["Q02值状态"]
        if status in ENUMS["Q02值状态"] and (status == "已记录") != bool(row["业务值"]):
            errors.append(f"{at} 业务值与Q02值状态不符（仅“已记录”填写业务值）")
        references = [row["主证据ID"], *re.split(r"[,，、]", row["旁证ID"])]
        for ref in filter(None, (item.strip() for item in references)):
            key = (row["批次"], row["会话"], ref)
            if key not in sources:
                errors.append(f"{at} 同批次同会话找不到原文ID“{ref}”")
            covered.add(key)
    for key, (at, note) in sources.items():
        if key not in covered and not note:
            errors.append(f"{at} 未被标签引用，需填写处理说明")
    return errors, len(sources), count


def main():
    parser = argparse.ArgumentParser(description="创建或检查导购试吃标注工作簿")
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("init", help="新建空白模板").add_argument("file", type=Path)
    audit = commands.add_parser("check", help="只读校验回链、字段、质量状态与原文覆盖")
    audit.add_argument("file", type=Path)
    audit.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA,
                       help="六列字段表（第5列为代码和名称）；质量枚举及空值规则按 V0.2 校验")
    args = parser.parse_args()
    try:
        if args.action == "init":
            create(args.file)
            print(f"已创建 {args.file}")
            return 0
        codes = field_codes(args.schema)
        book = load_workbook(args.file, read_only=True)
        try:
            errors, source_count, tag_count = check(book, codes)
        finally:
            book.close()
        for error in errors:
            print(error, file=sys.stderr)
        print(f"原文 {source_count} 条，标签 {tag_count} 条，结构校验发现 {len(errors)} 项问题。")
        return int(bool(errors))
    except FileExistsError:
        print(f"目标已存在，请指定新文件名：{args.file}", file=sys.stderr)
    except (OSError, ValueError, BadZipFile, InvalidFileException) as error:
        print(f"无法完成：{error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
