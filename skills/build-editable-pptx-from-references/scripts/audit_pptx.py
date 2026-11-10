#!/usr/bin/env python3
"""Read-only OOXML evidence report; it does not render or certify a slide deck."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import posixpath
import sys
import xml.etree.ElementTree as ET
from zipfile import BadZipFile, ZipFile


CLAIM_BOUNDARY = (
    "This is a structural OOXML inspection, not a visual or semantic certification. "
    "Object counts cannot prove that all intended content is editable: even a deck "
    "with native text may contain flattened body content. It does not render, "
    "perform OCR, resolve all inherited/theme formatting or group transforms, "
    "verify font installation, check factual accuracy, or open Microsoft PowerPoint. "
    "A pass means only that readable package evidence satisfied the explicit CLI "
    "requirements; visual comparison and content/source review remain necessary."
)


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def attr_local(element: ET.Element, name: str) -> str | None:
    return next((v for k, v in element.attrib.items() if k.endswith("}" + name)), None)


def relation_part(part: str) -> str:
    directory, basename = posixpath.split(part)
    return posixpath.join(directory, "_rels", basename + ".rels")


def target_part(owner: str, target: str) -> str:
    return posixpath.normpath(
        target.lstrip("/") if target.startswith("/") else posixpath.join(posixpath.dirname(owner), target)
    )


def text_of(element: ET.Element) -> str:
    return "".join(n.text or "" for n in element.iter() if local_name(n.tag) == "t")


def nonempty_paragraphs(root: ET.Element) -> list[ET.Element]:
    return [n for n in root.iter() if local_name(n.tag) == "p" and text_of(n).strip()]


def spacing_evidence(paragraphs: list[ET.Element]) -> dict:
    multiples: Counter[str] = Counter()
    points: Counter[str] = Counter()
    missing = malformed = 0
    for p in paragraphs:
        ln = p.find("./{*}pPr/{*}lnSpc")
        if ln is None:
            missing += 1
            continue
        pct, pts = ln.find("./{*}spcPct"), ln.find("./{*}spcPts")
        try:
            if pct is not None and pts is None:
                multiples[f"{int(pct.attrib['val']) / 100000:g}"] += 1
            elif pts is not None and pct is None:
                points[f"{int(pts.attrib['val']) / 100:g}"] += 1
            else:
                malformed += 1
        except (KeyError, ValueError):
            malformed += 1
    return {
        "text_paragraphs": len(paragraphs),
        "explicit_multiples": dict(sorted(multiples.items())),
        "explicit_fixed_points": dict(sorted(points.items())),
        "missing_explicit_spacing": missing,
        "malformed_explicit_spacing": malformed,
        "scope": "Nonempty paragraphs encoded in the slide XML, including table cells; inherited formatting, notes, masters and referenced chart text are excluded.",
    }


def image_geometry(pic: ET.Element, slide_size: tuple[int, int], grouped: bool) -> dict:
    result = {"group_transform_unresolved": grouped, "full_slide_candidate": False}
    xfrm = pic.find("./{*}spPr/{*}xfrm")
    if xfrm is None:
        result["geometry"] = "not_explicit"
        return result
    off, ext = xfrm.find("./{*}off"), xfrm.find("./{*}ext")
    try:
        x, y = int(off.attrib["x"]), int(off.attrib["y"])
        w, h = int(ext.attrib["cx"]), int(ext.attrib["cy"])
        rotation = int(xfrm.get("rot", "0"))
    except (AttributeError, KeyError, ValueError):
        result["geometry"] = "unreadable"
        return result
    result["frame_emu"] = {"x": x, "y": y, "cx": w, "cy": h, "rotation_60000deg": rotation}
    sw, sh = slide_size
    if not grouped and rotation % 21600000 == 0 and sw > 0 and sh > 0:
        overlap = max(0, min(x + w, sw) - max(x, 0)) * max(0, min(y + h, sh) - max(y, 0))
        result["slide_coverage_fraction"] = round(overlap / (sw * sh), 6)
        result["full_slide_candidate"] = overlap / (sw * sh) >= 0.90
    crop = pic.find("./{*}blipFill/{*}srcRect")
    result["crop_rect"] = dict(crop.attrib) if crop is not None else None
    return result


def audit(path: Path, args: argparse.Namespace) -> dict:
    report = {
        "schema_version": "editable-pptx-structure.v1",
        "file": str(path.resolve()),
        "pass": False,
        "errors": [],
        "warnings": [],
        "claim_boundary": CLAIM_BOUNDARY,
        "slides": [],
    }
    errors, warnings = report["errors"], report["warnings"]

    def fail(code: str, **details) -> None:
        errors.append({"code": code, **details})

    try:
        with path.open("rb") as handle:
            digest = hashlib.sha256()
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
            report["file_sha256"] = digest.hexdigest()
        with ZipFile(path) as z:
            names = set(z.namelist())
            cache: dict[str, ET.Element] = {}

            def xml(part: str) -> ET.Element:
                if part not in cache:
                    cache[part] = ET.fromstring(z.read(part))
                return cache[part]

            def relations(owner: str) -> dict[str, dict]:
                rp = relation_part(owner)
                if rp not in names:
                    return {}
                return {
                    e.attrib["Id"]: dict(e.attrib)
                    for e in xml(rp)
                    if local_name(e.tag) == "Relationship" and "Id" in e.attrib
                }

            pres = xml("ppt/presentation.xml")
            if local_name(pres.tag) != "presentation":
                raise ValueError("ppt/presentation.xml is not a presentation document")
            sz = pres.find("./{*}sldSz")
            slide_size = (int(sz.attrib["cx"]), int(sz.attrib["cy"])) if sz is not None else (0, 0)
            report["slide_size_emu"] = {"cx": slide_size[0], "cy": slide_size[1]}
            report["aspect_ratio"] = slide_size[0] / slide_size[1] if slide_size[1] else None
            if min(slide_size) <= 0:
                fail("invalid_or_missing_slide_size")
            pres_rels = relations("ppt/presentation.xml")
            order = pres.findall("./{*}sldIdLst/{*}sldId")
            report["slide_count"] = len(order)
            if not order:
                fail("missing_slide_order")
            if args.expected_slides is not None and len(order) != args.expected_slides:
                fail("slide_count_mismatch", expected=args.expected_slides, actual=len(order))

            # Report all concrete declarations separately from theme references.
            families: Counter[str] = Counter()
            theme_refs: Counter[str] = Counter()
            for part in sorted(names):
                if not (part.startswith("ppt/") and part.endswith(".xml")):
                    continue
                for e in xml(part).iter():
                    name = e.get("typeface", "").strip()
                    if name.startswith("+"):
                        theme_refs[name] += 1
                    elif name:
                        families[name] += 1
            report["explicit_font_families"] = sorted(families)
            report["explicit_font_declaration_counts"] = dict(sorted(families.items()))
            report["theme_font_references"] = dict(sorted(theme_refs.items()))
            report["font_scope"] = "Every concrete typeface declaration in ppt/*.xml parts, including themes and unused layouts; this is not a resolved list of fonts visibly used."
            if args.allowed_fonts is not None:
                extra = sorted(set(families) - args.allowed_fonts)
                if extra:
                    fail("font_outside_allowlist", fonts=extra)
                if theme_refs:
                    warnings.append({"code": "theme_or_inherited_fonts_not_fully_resolved", "message": "The font allowlist checks concrete declarations only; it does not establish effective fonts or installation."})

            for number, sid in enumerate(order, 1):
                rid = attr_local(sid, "id")
                rel = pres_rels.get(rid or "")
                if not rel or rel.get("TargetMode") == "External" or not rel.get("Type", "").endswith("/slide"):
                    fail("invalid_slide_relationship", slide=number, relationship_id=rid)
                    continue
                part = target_part("ppt/presentation.xml", rel["Target"])
                root = xml(part)
                parent = {child: node for node in root.iter() for child in node}
                shapes = root.findall(".//{*}sp")
                connectors = root.findall(".//{*}cxnSp")
                native_text = [s for s in shapes if text_of(s).strip()]
                pictures = root.findall(".//{*}pic")
                tables = root.findall(".//{*}tbl")
                frames = root.findall(".//{*}graphicFrame")
                charts = root.findall(".//{*}chart")
                paragraphs = nonempty_paragraphs(root)
                spacing = spacing_evidence(paragraphs)
                row = {
                    "slide": number,
                    "part": part,
                    "native_text_shapes": len(native_text),
                    "native_nontext_shapes": len(shapes) - len(native_text) + len(connectors),
                    "native_shape_total": len(shapes) + len(connectors),
                    "connectors": len(connectors),
                    "groups": len(root.findall(".//{*}grpSp")),
                    "pictures": len(pictures),
                    "tables": len(tables),
                    "table_dimensions": [{"rows": len(t.findall("./{*}tr")), "columns": len(t.findall("./{*}tblGrid/{*}gridCol"))} for t in tables],
                    "charts": len(charts),
                    "graphic_frames": len(frames),
                    "native_text_characters": sum(len(text_of(s).strip()) for s in native_text),
                    "slide_text_characters": sum(len(text_of(p).strip()) for p in paragraphs),
                    "line_spacing": spacing,
                    "notes_present": False,
                    "notes_characters": 0,
                    "images": [],
                }
                report["slides"].append(row)
                rels = relations(part)
                for pic in pictures:
                    node = parent.get(pic)
                    grouped = False
                    while node is not None:
                        if local_name(node.tag) == "grpSp":
                            grouped = True
                            break
                        node = parent.get(node)
                    props = pic.find("./{*}nvPicPr/{*}cNvPr")
                    ev = image_geometry(pic, slide_size, grouped)
                    ev["name"] = props.get("name") if props is not None else None
                    blip = pic.find("./{*}blipFill/{*}blip")
                    irid = attr_local(blip, "embed") if blip is not None else None
                    irel = rels.get(irid or "")
                    if irel and irel.get("TargetMode") != "External":
                        ev["media_part"] = target_part(part, irel["Target"])
                    elif blip is not None and attr_local(blip, "link"):
                        ev["external_image"] = True
                    row["images"].append(ev)
                if any(i["full_slide_candidate"] for i in row["images"]) and row["native_text_characters"] < 80 and not tables and not charts:
                    warnings.append({"code": "full_slide_image_with_sparse_native_text", "slide": number, "message": "A picture covers at least 90% of the slide with fewer than 80 native text characters. It may be a normal background/photo or flattened content; inspect visually. This warning alone is not a failure."})
                if number in args.required_table_slides and not tables:
                    fail("required_native_table_missing", slide=number)
                if args.line_spacing is not None:
                    wrong = {v: n for v, n in spacing["explicit_multiples"].items() if not math.isclose(float(v), args.line_spacing, abs_tol=0.00001)}
                    if wrong or spacing["explicit_fixed_points"] or spacing["missing_explicit_spacing"] or spacing["malformed_explicit_spacing"]:
                        fail("explicit_line_spacing_requirement_not_met", slide=number, expected_multiple=args.line_spacing, evidence=spacing)
                notes_rels = [r for r in rels.values() if r.get("Type", "").endswith("/notesSlide") and r.get("TargetMode") != "External"]
                for nr in notes_rels:
                    npart = target_part(part, nr["Target"])
                    nroot = xml(npart)
                    note_texts = []
                    for s in nroot.findall(".//{*}sp"):
                        ph = s.find("./{*}nvSpPr/{*}nvPr/{*}ph")
                        if ph is not None and ph.get("type") in {"sldImg", "sldNum", "dt", "hdr", "ftr"}:
                            continue
                        note_texts.extend(text_of(p).strip() for p in nonempty_paragraphs(s))
                    row["notes_present"] = True
                    row["notes_part"] = npart
                    row["notes_characters"] += sum(len(t) for t in note_texts)
                if args.require_notes and not row["notes_characters"]:
                    fail("required_speaker_notes_missing_or_empty", slide=number)

            for number in sorted(args.required_table_slides):
                if number > len(order):
                    fail("required_table_slide_out_of_range", slide=number, slide_count=len(order))
            report["media"] = [
                {"part": name, "bytes": z.getinfo(name).file_size, "sha256": hashlib.sha256(z.read(name)).hexdigest()}
                for name in sorted(names) if name.startswith("ppt/media/") and not name.endswith("/")
            ]
            report["notes_slides_with_text"] = sum(s["notes_characters"] > 0 for s in report["slides"])
    except (OSError, BadZipFile, KeyError, ValueError, ET.ParseError, RuntimeError) as exc:
        fail("package_read_error", exception=type(exc).__name__, message=str(exc))
    report["pass"] = not errors
    return report


def parse_slide_set(value: str) -> set[int]:
    try:
        result = {int(x.strip()) for x in value.split(",") if x.strip()}
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use comma-separated positive, 1-based slide numbers.") from exc
    if any(x <= 0 for x in result):
        raise argparse.ArgumentTypeError("Slide numbers are 1-based and must be positive.")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--expected-slides", type=int)
    parser.add_argument("--required-table-slides", type=parse_slide_set, default=set(), metavar="1,5")
    parser.add_argument("--allowed-fonts", help="Comma-separated allowlist of concrete font declarations; theme references remain unresolved.")
    parser.add_argument("--require-notes", action="store_true")
    parser.add_argument("--line-spacing", type=float, help="Require this explicit line-spacing multiple in every nonempty slide paragraph; inherited/fixed-point spacing does not satisfy it.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.expected_slides is not None and args.expected_slides < 1:
        parser.error("--expected-slides must be positive")
    if args.line_spacing is not None and (not math.isfinite(args.line_spacing) or args.line_spacing <= 0):
        parser.error("--line-spacing must be a positive finite multiple")
    if args.output is not None:
        same_path = args.output.resolve() == args.pptx.resolve()
        same_file = args.output.exists() and args.pptx.exists() and args.output.samefile(args.pptx)
        if same_path or same_file:
            parser.error("--output must not overwrite the input PPTX")
    if args.allowed_fonts is not None:
        args.allowed_fonts = {x.strip() for x in args.allowed_fonts.split(",") if x.strip()}
        if not args.allowed_fonts:
            parser.error("--allowed-fonts must contain at least one font name")
    report = audit(args.pptx, args)
    content = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")
    sys.stdout.write(content)
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
