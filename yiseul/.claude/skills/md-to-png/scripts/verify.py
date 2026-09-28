#!/usr/bin/env python3
"""Check that every element of a Markdown file made it into the rendered page and the PNG.

Usage:
    python verify.py <input.md> <output.png> [--width 900] [--scale 2] [--browser PATH]

Expected elements are parsed from the Markdown source (headings, list items, images,
links, horizontal rules, every line of text) and compared with the DOM that headless
Chrome rendered. The PNG size is compared with the rendered page size to catch cropping.
Exit code is 1 when any check fails.
"""
import argparse
import html
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from md_to_png import find_browser, prepare, render_report  # noqa: E402

TAG = re.compile(r"<[^>]+>")
MD_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
HTML_HEADING = re.compile(r"<h([1-6])[^>]*>(.*?)</h\1>", re.S | re.I)
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.*)$")
HR = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$")
HTML_IMG = re.compile(r"<img[^>]*?\bsrc\s*=\s*\"([^\"]+)\"", re.I)
MD_IMG = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")
HTML_A = re.compile(r"<a[^>]*?\bhref\s*=\s*\"([^\"]+)\"", re.I)
MD_A = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)")


def plain(s):
    """Markdown/HTML inline -> the text a browser would show."""
    s = TAG.sub("", s)
    s = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"(\*\*|__|~~|`)", "", s)
    s = re.sub(r"(?<!\w)\*(\S[^*]*?)\*", r"\1", s)
    return " ".join(html.unescape(s).split())


def raw(s):
    """Same text with Markdown markers kept — what shows when emphasis fails to parse."""
    return " ".join(html.unescape(TAG.sub("", s)).split())


def classify(items, haystack):
    """Split expected (plain, raw) pairs into missing and shown-with-literal-markup."""
    literal = [r for p, r in items if p not in haystack and r in haystack]
    missing = [p for p, r in items if p not in haystack and r not in haystack]
    return missing, literal


def expected_from_md(md):
    exp = {"headings": [], "listItems": [], "images": [], "links": [], "hrCount": 0, "texts": []}
    in_fence = False
    prev_blank = True
    for line in md.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence  # fence markers themselves are not rendered
            continue
        if in_fence:
            code = " ".join(line.split())
            if code:
                exp["texts"].append((code, code))
            continue
        exp["images"] += HTML_IMG.findall(line) + MD_IMG.findall(line)
        exp["links"] += HTML_A.findall(line) + MD_A.findall(line)
        if m := MD_HEADING.match(line):
            exp["headings"].append({"tag": f"h{len(m.group(1))}", "text": plain(m.group(2))})
        elif HR.match(line) and prev_blank:
            exp["hrCount"] += 1
        elif m := LIST_ITEM.match(line):
            exp["listItems"].append((plain(m.group(1)), raw(m.group(1))))
        body = MD_HEADING.sub(r"\2", LIST_ITEM.sub(r"\1", line))
        if plain(body) and not HR.match(line):
            exp["texts"].append((plain(body), raw(body)))
        prev_blank = not line.strip()
    for level, inner in HTML_HEADING.findall(md):
        exp["headings"].append({"tag": f"h{level}", "text": plain(inner)})
    return exp


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("png")
    ap.add_argument("--width", type=int, default=900)
    ap.add_argument("--scale", type=float, default=2)
    ap.add_argument("--browser")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    browser = find_browser(args.browser)
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as work:
        md_text, html_path = prepare(args.input, args.width, work)
        dom = render_report(browser, html_path, args.width)
    exp = expected_from_md(md_text)

    results = []
    warnings = []

    def check(name, ok, detail=""):
        results.append(ok)
        print(f"{'✅' if ok else '❌'} {name}" + (f" — {detail}" if detail else ""))

    def check_texts(name, items, haystack):
        missing, literal = classify(items, haystack)
        check(f"{name} {len(items)}개", not missing, f"누락: {missing}" if missing else "모두 포함")
        for r in literal:
            warnings.append(r)
            print(f"   ⚠️ 마크다운 기호가 그대로 표시됨(원본 문법 문제, GitHub도 동일): {r}")

    # Headings
    dom_heads = Counter((h["tag"], h["text"]) for h in dom["headings"])
    exp_heads = Counter((h["tag"], h["text"]) for h in exp["headings"])
    missing = exp_heads - dom_heads
    check(f"헤딩 {sum(exp_heads.values())}개", not missing,
          f"누락: {list(missing)}" if missing else ", ".join(f"{t}:{x}" for t, x in exp_heads))

    # List items
    check_texts("리스트 항목", exp["listItems"], dom["listItems"])

    # Images present and loaded
    missing = Counter(exp["images"]) - Counter(i["src"] for i in dom["images"])
    check(f"이미지(뱃지) {len(exp['images'])}개 포함", not missing,
          f"누락: {list(missing)}" if missing else f"렌더됨 {len(dom['images'])}개")
    failed = [i["src"] for i in dom["images"] if not i["loaded"]]
    check("이미지 로딩 성공", not failed, f"실패: {failed}" if failed else "모두 로딩됨")

    # Links
    missing = Counter(exp["links"]) - Counter(dom["links"])
    check(f"링크 {len(exp['links'])}개", not missing, f"누락: {list(missing)}" if missing else ", ".join(exp["links"]))

    # Horizontal rules
    check(f"구분선(hr) {exp['hrCount']}개", dom["hrCount"] == exp["hrCount"], f"렌더됨 {dom['hrCount']}개")

    # Every text line
    check_texts("텍스트 라인", exp["texts"], dom["text"])

    # PNG vs page size (catches cropping)
    size = png_size(args.png)
    want = (round(args.width * args.scale), round(dom["height"] * args.scale))
    ok = size is not None and abs(size[0] - want[0]) <= 2 and abs(size[1] - want[1]) <= 2 * args.scale
    check("PNG 크기 = 렌더 페이지 전체(잘림 없음)", ok, f"PNG {size}, 기대 {want}")

    passed = sum(results)
    print(f"\n결과: {passed}/{len(results)} 통과" + (f", 경고 {len(set(warnings))}건" if warnings else ""))
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
