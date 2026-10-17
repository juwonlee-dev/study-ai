#!/usr/bin/env python3
"""Render a Markdown file GitHub-style in headless Chrome/Edge and save it as a PNG.

Usage:
    python md_to_png.py <input.md> <output.png> [--width 900] [--scale 2] [--browser PATH]

Only the Python standard library and an installed Chrome/Edge are needed.
marked (Markdown -> HTML) and github-markdown-css are loaded from jsdelivr at render time.
"""
import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MARKED_JS = "https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"
GITHUB_CSS = "https://cdn.jsdelivr.net/npm/github-markdown-css@5.5.1/github-markdown-light.css"

BROWSER_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]
BROWSER_NAMES = ["google-chrome", "chrome", "chromium", "chromium-browser", "msedge", "microsoft-edge"]

PAGE_TEMPLATE = """<!doctype html>
<html><head><meta charset="utf-8">
<link rel="stylesheet" href="__CSS__">
<style>
  html, body { margin: 0; background: #ffffff; }
  .markdown-body {
    box-sizing: border-box; width: __WIDTH__px; padding: 40px 45px;
    font-family: -apple-system, "Segoe UI", "Malgun Gothic", "Apple SD Gothic Neo", "Noto Sans KR",
                 Helvetica, Arial, sans-serif, "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji";
  }
</style>
<script src="__MARKED__"></script>
</head><body>
<article class="markdown-body" id="content"></article>
<pre id="__result" style="display:none"></pre>
<script>
const md = __MD_JSON__;
const content = document.getElementById('content');
content.innerHTML = marked.parse(md, { gfm: true });
const imgs = [...content.querySelectorAll('img')];
const waitImg = i => i.complete ? Promise.resolve() : new Promise(r => { i.onload = r; i.onerror = r; });
Promise.all(imgs.map(waitImg)).then(() => {
  const norm = s => s.replace(/\\s+/g, ' ').trim();
  const report = {
    height: Math.ceil(content.getBoundingClientRect().height),
    headings: [...content.querySelectorAll('h1,h2,h3,h4,h5,h6')]
      .map(h => ({ tag: h.tagName.toLowerCase(), text: norm(h.innerText) })),
    listItems: [...content.querySelectorAll('li')].map(l => norm(l.innerText)),
    images: imgs.map(i => ({ src: i.getAttribute('src'), loaded: i.complete && i.naturalWidth > 0,
                             w: i.naturalWidth, h: i.naturalHeight })),
    links: [...content.querySelectorAll('a')].map(a => a.getAttribute('href')),
    hrCount: content.querySelectorAll('hr').length,
    text: norm(content.innerText),
  };
  document.getElementById('__result').textContent = JSON.stringify(report);
});
</script>
</body></html>
"""


def find_browser(explicit=None):
    if explicit:
        return explicit
    for path in BROWSER_CANDIDATES:
        if os.path.exists(path):
            return path
    for name in BROWSER_NAMES:
        found = shutil.which(name)
        if found:
            return found
    sys.exit("Chrome/Edge를 찾을 수 없습니다. --browser 로 경로를 지정하세요.")


def build_page(md_text, width):
    # "</" is escaped so Markdown containing </script> cannot break out of the script tag.
    md_json = json.dumps(md_text, ensure_ascii=False).replace("</", "<\\/")
    return (PAGE_TEMPLATE.replace("__CSS__", GITHUB_CSS)
            .replace("__MARKED__", MARKED_JS)
            .replace("__WIDTH__", str(width))
            .replace("__MD_JSON__", md_json))


def run_browser(browser, html_path, extra_args):
    # A throwaway profile keeps headless Chrome from attaching to the user's running browser.
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as profile:
        cmd = [browser, "--headless=new", "--disable-gpu", "--no-first-run",
               "--no-default-browser-check", f"--user-data-dir={profile}",
               "--hide-scrollbars", "--virtual-time-budget=15000",
               *extra_args, Path(html_path).resolve().as_uri()]
        return subprocess.run(cmd, capture_output=True, timeout=180)


def render_report(browser, html_path, width):
    """Load the page and return the JSON report the page writes after all images settle."""
    proc = run_browser(browser, html_path, ["--dump-dom", f"--window-size={width},1000"])
    dom = proc.stdout.decode("utf-8", errors="replace")
    m = re.search(r'<pre id="__result"[^>]*>(.*?)</pre>', dom, re.S)
    if not m or not m.group(1).strip():
        sys.exit("렌더링 결과를 읽지 못했습니다 (네트워크/CDN 접근 확인 필요).\n"
                 + proc.stderr.decode("utf-8", errors="replace")[-2000:])
    return json.loads(html.unescape(m.group(1)))


def prepare(md_path, width, workdir):
    md_text = Path(md_path).read_text(encoding="utf-8")
    html_path = Path(workdir) / "render.html"
    html_path.write_text(build_page(md_text, width), encoding="utf-8")
    return md_text, html_path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--width", type=int, default=900, help="page width in CSS px (default 900)")
    ap.add_argument("--scale", type=float, default=2, help="device scale factor (default 2)")
    ap.add_argument("--browser")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    browser = find_browser(args.browser)
    out = Path(args.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as work:
        _, html_path = prepare(args.input, args.width, work)
        report = render_report(browser, html_path, args.width)
        run_browser(browser, html_path, [
            f"--screenshot={out}",
            f"--window-size={args.width},{report['height']}",
            f"--force-device-scale-factor={args.scale}",
        ])

    if not out.exists():
        sys.exit("스크린샷 생성 실패")
    failed = [i["src"] for i in report["images"] if not i["loaded"]]
    print(json.dumps({
        "output": str(out),
        "cssHeight": report["height"],
        "images": len(report["images"]),
        "failedImages": failed,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
