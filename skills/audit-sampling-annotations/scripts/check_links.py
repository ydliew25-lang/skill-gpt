#!/usr/bin/env python3
"""Audit copied source rows, evidence links and value states in a normalized batch."""
import argparse
from collections import defaultdict
import json
import sys


def text(value):
    return isinstance(value, str) and bool(value.strip())


def strings(value):
    return isinstance(value, list) and all(text(item) for item in value)


def check_input(data):
    if not isinstance(data, dict):
        raise ValueError("expected an object with raw, copied and labels arrays")
    for table in ("raw", "copied", "labels"):
        rows = data.get(table)
        if not isinstance(rows, list):
            raise ValueError(f"{table}: expected an array")
        for n, row in enumerate(rows, 1):
            where = f"{table}[{n}]"
            if not isinstance(row, dict):
                raise ValueError(f"{where}: expected a row object")
            for key in ("id", "session"):
                if not text(row.get(key)):
                    raise ValueError(f"{where}.{key}: expected a nonblank string")
            if table in ("raw", "copied") and not isinstance(row.get("text"), str):
                raise ValueError(f"{where}.text: expected the exact source string")
            if table == "raw" and not strings(row.get("shared_with", [])):
                raise ValueError(f"{where}.shared_with: expected an array of session IDs")


def index(rows):
    result = defaultdict(list)
    for row in rows:
        result[row["id"]].append(row)
    return result


def metric(numerator, denominator):
    return {"numerator": numerator, "denominator": denominator,
            "rate": numerator / denominator if denominator else None}


def audit(data):
    check_input(data)
    raw, copied, labels = (data[k] for k in ("raw", "copied", "labels"))
    problems = []

    def flag(code, **details):
        problems.append({"code": code, **details})

    original, replica = index(raw), index(copied)
    for table, indexed in (("raw", original), ("copied", replica), ("labels", index(labels))):
        for row_id, entries in indexed.items():
            if len(entries) > 1:
                flag("duplicate_id", table=table, id=row_id, count=len(entries))

    exact = 0
    for key, originals in original.items():
        copies = replica.get(key, [])
        if not copies:
            flag("missing_copy", id=key)
        if len(originals) == len(copies) == 1:
            differences = [k for k in ("text", "session") if originals[0][k] != copies[0][k]]
            if differences:
                flag("copy_changed", id=key, fields=differences)
            else:
                exact += 1
    for key in replica.keys() - original.keys():
        flag("extra_copy", id=key)

    linked = consistent = 0
    for number, label in enumerate(labels, 1):
        location = {"id": label["id"], "label_row": number}
        before = len(problems)
        groups = (("primary", [label.get("primary")]), ("support", label.get("support", [])))
        for kind, refs in groups:
            if not strings(refs):
                flag("invalid_evidence_reference", kind=kind, **location)
                continue
            for ref in refs:
                matches = original.get(ref, [])
                if len(matches) != 1:
                    code = "missing_evidence" if not matches else "ambiguous_evidence"
                    flag(code, kind=kind, evidence=ref, **location)
                elif label["session"] != matches[0]["session"] and label["session"] not in matches[0].get("shared_with", []):
                    flag("cross_session_evidence", kind=kind, evidence=ref, **location)
        linked += len(problems) == before

        before = len(problems)
        status = label.get("status")
        if status not in ("recorded", "missing"):
            flag("invalid_status", **location)
        if "value" not in label:
            flag("absent_value_key", **location)
        elif status == "recorded":
            v = label["value"]
            if v is None or (isinstance(v, str) and not text(v)):
                flag("recorded_without_value", **location)
        elif status == "missing" and label["value"] is not None:
            flag("missing_with_value", **location)
        if status == "missing" and not text(label.get("reason")):
            flag("missing_without_reason", **location)
        consistent += len(problems) == before

    metrics = {"raw_rows_copied_exactly_once": metric(exact, len(raw)),
               "label_rows_with_resolvable_in_scope_evidence": metric(linked, len(labels)),
               "label_rows_with_consistent_value_state": metric(consistent, len(labels))}
    return {"scope": "normalized structural checks only",
            "rows": {"raw": len(raw), "copied": len(copied), "labels": len(labels)},
            "metrics": metrics, "issue_count": len(problems), "issues": problems}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="JSON path, or - for stdin")
    args = parser.parse_args()
    try:
        if args.input == "-":
            data = json.load(sys.stdin)
        else:
            with open(args.input, encoding="utf-8") as handle:
                data = json.load(handle)
        result = audit(data)
    except (ValueError, OSError) as error:
        print(json.dumps({"input_error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(bool(result["issues"]))


if __name__ == "__main__":
    sys.exit(main())
