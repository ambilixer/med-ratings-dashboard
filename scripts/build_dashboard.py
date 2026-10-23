"""Build the standalone dashboard: docs/index.html (served by GitHub Pages).

Usage (from anywhere):
  python scripts/build_dashboard.py

Inlines everything into one file, so the page works offline and needs no server:
  dashboard/shell.html          page wrapper: theme colors, footer, and a small `dash` runtime
  dashboard/page.html           the dashboard itself (markup, styles, chart code)
  dashboard/vendor/d3.*.min.js  d3 v7 charting library
  dashboard/fonts/*.woff        Fira Sans, Latin subset (SIL Open Font License)
  data/drugscom_ratings_long.csv
"""
import re
import base64
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO_URL = "https://github.com/ambilixer/med-ratings-dashboard"
DATA_DATES = "October 22 and 23, 2026"

SHELL = ROOT / "dashboard" / "shell.html"
PAGE = ROOT / "dashboard" / "page.html"
DATA = ROOT / "data" / "drugscom_ratings_long.csv"
OUT = ROOT / "docs" / "index.html"
FONTS = {400: "fira-sans-latin-400.woff", 500: "fira-sans-latin-500.woff"}


def font_faces():
    """@font-face rules with the font files inlined, so the page makes no outside requests."""
    rules = []
    for weight, name in FONTS.items():
        b64 = base64.b64encode((ROOT / "dashboard" / "fonts" / name).read_bytes()).decode("ascii")
        rules.append(
            '@font-face { font-family: "Fira Sans"; font-style: normal; font-weight: %d; font-display: swap; '
            'src: url(data:font/woff;base64,%s) format("woff"); }' % (weight, b64)
        )
    return "\n".join(rules)


def read(p):
    return p.read_text(encoding="utf-8")


def main():
    shell, page = read(SHELL), read(PAGE)
    d3_files = sorted((ROOT / "dashboard" / "vendor").glob("d3.*.min.js"))
    assert len(d3_files) == 1, f"expected one d3 build in dashboard/vendor, found {d3_files}"
    d3 = read(d3_files[0])
    csv = read(DATA).strip().replace("\r\n", "\n")
    assert "</" not in csv, "data contains '</', which would break the inline <script>"

    # The page's scripts call `dash` and `d3`, so they move after the runtime; markup and styles stay in place.
    script_re = re.compile(r"<script\b[^>]*>.*?</script>", re.S)
    page_scripts = "\n".join(script_re.findall(page))
    page_body = script_re.sub("", page).strip()
    assert page_scripts, "no <script> found in dashboard/page.html"

    html = shell
    for token, value in {
        "<!--FONTS-->": font_faces(),
        "<!--PAGE-->": page_body,
        "<!--PAGE_SCRIPTS-->": page_scripts,
        "<!--DATA_CSV-->": csv,
        "<!--D3-->": d3,
        "<!--REPO_URL-->": REPO_URL,
        "<!--DATA_DATES-->": DATA_DATES,
        "<!--BUILD_DATE-->": dt.date.today().strftime("%B %d, %Y").replace(" 0", " "),
    }.items():
        assert html.count(token) == 1, f"{token} should appear exactly once in shell.html"
        html = html.replace(token, value)

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html, encoding="utf-8", newline="\n")
    (OUT.parent / ".nojekyll").touch()
    rows = csv.count("\n")
    print(f"Wrote {OUT.relative_to(ROOT)} ({len(html.encode('utf-8')) / 1024:.0f} KB, {rows} data rows)")


if __name__ == "__main__":
    main()
