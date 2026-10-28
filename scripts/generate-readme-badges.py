#!/usr/bin/env python3
"""Generate a live "at a glance" SVG banner + shields.io badge URLs for the README.

Reads prompts.js (the source of truth), counts real numbers, and writes:
  - assets/readme-banner.svg      : hero banner with live stats (prompts, categories...)
  - assets/prompt-map.svg         : category bar chart ("the prompt map")
  - assets/README-BADGES.md       : ready-to-paste shields.io badge markdown
  - assets/PROMPT-LIBRARY-SECTION.md : full showcase block for the profile README
  - assets/profile-README.md      : if it exists, the "## 🧠 Prompt Library" section
                                    inside it is refreshed in place (your full
                                    profile template, kept always up to date)

Run it after editing prompts.js, or let GitHub Actions do it automatically.
Usage: python3 scripts/generate-readme-badges.py
"""
from __future__ import annotations

import json
import os
import re
import urllib.parse
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPTS_JS = os.path.join(ROOT, "prompts.js")
ASSETS_DIR = os.path.join(ROOT, "assets")

# ---------------------------------------------------------------- label -> color
LABEL_COLORS = {
    "QA Architect": "#E8590C",
    "Business Analyst": "#1D9E75",
    "QA Management": "#7F77DD",
    "Data Engineer": "#2E86DE",
    "Meta": "#EA4335",
    "Oracle": "#B07A2A",
    "Senior QA": "#D4A017",
    "Analysis": "#5CA4FF",
    "General": "#8D99AE",
    "Performance": "#9C3498",
    "Security": "#C0392B",
}
FALLBACK_COLOR = "#8D99AE"


def load_prompts() -> list[dict]:
    """Extract the prompt objects from `const PROMPTS = [...]` without needing node.

    Decodes object-by-object so a trailing comma (valid JS, invalid JSON) is fine.
    """
    src = open(PROMPTS_JS, encoding="utf-8").read()
    start = src.index("const PROMPTS = [") + len("const PROMPTS = ")
    body = src[start:]
    decoder = json.JSONDecoder()
    pos = body.index("[") + 1
    items: list[dict] = []
    while pos < len(body):
        while pos < len(body) and body[pos] in " \n\t,":
            pos += 1
        if pos >= len(body) or body[pos] == "]":
            break
        obj, pos = decoder.raw_decode(body, pos)
        items.append(obj)
    return items


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def shield_url(label: str, message: str, color: str) -> str:
    q = lambda t: urllib.parse.quote(t.replace("-", "--").replace("_", "__"))
    return f"https://img.shields.io/badge/{q(label)}-{q(message)}-{color}?style=flat-square&labelColor=1A1B26"


# ---------------------------------------------------------------- banner SVG
def build_banner(stats: dict) -> str:
    W, H = 1280, 400
    cards = [
        ("🧩", f'{stats["total"]}', "prompts, battle-tested"),
        ("🗂️", f'{stats["categories"]}', "categories & counting"),
        ("📏", f'#{stats["max_number"]}', "highest prompt number"),
        ("✨", f'{stats["words"]:,}', "words of pure prompt craft"),
    ]
    card_w, card_h, gap = 270, 150, 30
    total_w = len(cards) * card_w + (len(cards) - 1) * gap
    x0 = (W - total_w) // 2
    y0 = 190

    cards_svg = ""
    for i, (icon, big, small) in enumerate(cards):
        x = x0 + i * (card_w + gap)
        cards_svg += f"""
    <rect x="{x}" y="{y0}" width="{card_w}" height="{card_h}" rx="18" fill="#FFFFFF" fill-opacity="0.06" stroke="#FFFFFF" stroke-opacity="0.14"/>
    <text x="{x + 24}" y="{y0 + 46}" font-size="26">{icon}</text>
    <text x="{x + 24}" y="{y0 + 100}" font-family="'Segoe UI',Helvetica,Arial,sans-serif" font-size="42" font-weight="700" fill="#FFFFFF">{esc(big)}</text>
    <text x="{x + 24}" y="{y0 + 128}" font-family="'Segoe UI',Helvetica,Arial,sans-serif" font-size="15" fill="#9AA0C8">{esc(small)}</text>"""

    ticker = " · ".join(f"{n}× {lab}" for lab, n in stats["top_labels"])

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Prompt Library at a glance">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0F1021"/>
      <stop offset="55%" stop-color="#161735"/>
      <stop offset="100%" stop-color="#1E1440"/>
    </linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#7F77DD"/>
      <stop offset="50%" stop-color="#E8590C"/>
      <stop offset="100%" stop-color="#1D9E75"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.85" cy="0.1" r="0.7">
      <stop offset="0%" stop-color="#7F77DD" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#7F77DD" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glow2" cx="0.1" cy="0.95" r="0.6">
      <stop offset="0%" stop-color="#1D9E75" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="#1D9E75" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <rect width="{W}" height="{H}" rx="24" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" rx="24" fill="url(#glow)"/>
  <rect width="{W}" height="{H}" rx="24" fill="url(#glow2)"/>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="23" fill="none" stroke="url(#accent)" stroke-opacity="0.5" stroke-width="2"/>

  <text x="{W / 2}" y="86" text-anchor="middle" font-family="'Segoe UI',Helvetica,Arial,sans-serif" font-size="44" font-weight="800" fill="#FFFFFF">🧠 The Prompt Library</text>
  <text x="{W / 2}" y="124" text-anchor="middle" font-family="'Segoe UI',Helvetica,Arial,sans-serif" font-size="20" fill="#B8BEDD">An Automation Test Engineer's playground — QA · BA · Data · Oracle · Meta</text>

{cards_svg}

  <text x="{W / 2}" y="378" text-anchor="middle" font-family="'Segoe UI',Helvetica,Arial,sans-serif" font-size="14" fill="#7C83AD">{esc(ticker)}</text>
  <text x="{W - 20}" y="34" text-anchor="end" font-family="'Segoe UI',Helvetica,Arial,sans-serif" font-size="13" fill="#7C83AD">lhlhai.github.io/prompt-library ✦ auto-generated, always fresh</text>
</svg>
"""


# ---------------------------------------------------------------- prompt map
def build_prompt_map(counts: Counter, total: int) -> str:
    rows = counts.most_common()
    row_h, pad_top, left, right = 46, 74, 220, 340
    max_n = rows[0][1]
    bar_max = 700
    W = left + bar_max + right
    H = pad_top + len(rows) * row_h + 66

    bars = ""
    for i, (lab, n) in enumerate(rows):
        y = pad_top + i * row_h
        w = max(int(bar_max * n / max_n), 14)
        color = LABEL_COLORS.get(lab, FALLBACK_COLOR)
        pct = round(100 * n / total)
        bars += f"""
    <text x="{left - 14}" y="{y + 28}" text-anchor="end" font-family="'Segoe UI',Helvetica,Arial,sans-serif" font-size="16" fill="#C7CCE8">{esc(lab)}</text>
    <rect x="{left}" y="{y + 10}" width="{bar_max}" height="24" rx="12" fill="#FFFFFF" fill-opacity="0.05"/>
    <rect x="{left}" y="{y + 10}" width="{w}" height="24" rx="12" fill="{color}" fill-opacity="0.9"/>
    <text x="{left + w + 14}" y="{y + 28}" font-family="'Segoe UI',Helvetica,Arial,sans-serif" font-size="15" font-weight="700" fill="#FFFFFF">{n} <tspan fill="#8B92BC" font-weight="400">({pct}%)</tspan></text>"""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Prompt Library category map">
  <defs>
    <linearGradient id="mbg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0F1021"/>
      <stop offset="100%" stop-color="#191434"/>
    </linearGradient>
  </defs>
  <rect width="{W}" height="{H}" rx="20" fill="url(#mbg)"/>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="19" fill="none" stroke="#7F77DD" stroke-opacity="0.35"/>
  <text x="32" y="42" font-family="'Segoe UI',Helvetica,Arial,sans-serif" font-size="22" font-weight="800" fill="#FFFFFF">🗺️ The Prompt Map <tspan fill="#8B92BC" font-size="15" font-weight="400">— where the {total} prompts live</tspan></text>
{bars}
  <text x="32" y="{H - 24}" font-family="'Segoe UI',Helvetica,Arial,sans-serif" font-size="13" fill="#7C83AD">Auto-generated from prompts.js by scripts/generate-readme-badges.py — regenerate on every new prompt 🚀</text>
</svg>
"""


# ---------------------------------------------------------------- badges md
def build_badge_md(stats: dict, counts: Counter) -> str:
    lines = []
    add = lines.append
    add('[![Prompt Library](https://raw.githubusercontent.com/lhlhai/prompt-library/<BRANCH>/assets/readme-banner.svg)](https://lhlhai.github.io/prompt-library/)')
    add("")
    add("[![Prompts](%s)](https://github.com/lhlhai/prompt-library/blob/main/prompts.js)"
        % shield_url("prompts", str(stats["total"]), "7F77DD"))
    add("[![Categories](%s)](https://lhlhai.github.io/prompt-library/prompts.html)"
        % shield_url("categories", str(stats["categories"]), "1D9E75"))
    add("[![Prompt words](%s)](https://github.com/lhlhai/prompt-library)"
        % shield_url("prompt words", f'{stats["words"]:,}', "E8590C"))
    add("[![Lines of craft](%s)](https://github.com/lhlhai/prompt-library)"
        % shield_url("lines of craft", str(stats["js_lines"]), "2E86DE"))
    add("[![Live demo](%s)](https://lhlhai.github.io/prompt-library/)"
        % shield_url("live demo", "GitHub Pages", "EA4335"))
    add("[![Contribute](%s)](https://lhlhai.github.io/prompt-library/contribute.html)"
        % shield_url("contribute", "welcome", "D4A017"))
    add("")
    for lab, n in counts.most_common():
        add("[![%s](%s)](https://lhlhai.github.io/prompt-library/prompts.html)"
            % (lab, shield_url(lab, str(n), LABEL_COLORS.get(lab, FALLBACK_COLOR).lstrip("#"))))
    return "\n".join(lines) + "\n"


def build_section_md(stats: dict, counts: Counter) -> str:
    """Full showcase block for the profile README (lhlhai/lhlhai)."""
    badges = build_badge_md(stats, counts).replace("<BRANCH>", "main")
    lines = []
    add = lines.append
    add("## \U0001F9E0 Prompt Library — my playground of battle-tested prompts\n")
    add("*%s prompts for QA, BA & Data folks — copy, paste, ship.* ⚡\n" % stats["total"])
    add("<div align=\"center\">\n")
    add("[![Prompt Library](https://raw.githubusercontent.com/lhlhai/prompt-library/main/assets/readme-banner.svg)](https://lhlhai.github.io/prompt-library/)\n")
    # badge rows only (skip the banner line already added above)
    for ln in badges.splitlines():
        if ln.startswith("[![Prompt Library]"):
            continue
        add(ln)
    add("\n</div>\n")
    add("\U0001F5FA️ **The Prompt Map** — where all the prompts live:\n")
    add("<p align=\"center\">\n"
        "  <img src=\"https://raw.githubusercontent.com/lhlhai/prompt-library/main/assets/prompt-map.svg\" alt=\"Prompt Library category map\" width=\"100%\" />\n"
        "</p>\n")
    add("> \U0001F522 Every number above is **live**, auto-generated from `prompts.js` by GitHub Actions — this library never lies about its stats. \U0001F60C\n"
        "> \U0001F91D The first PR gets a permanent spot on the [Wall of Fame](https://lhlhai.github.io/prompt-library/contribute.html). Yes, there's a contributor personality quiz. You've been warned. \U0001F604\n")
    add("**[\U0001F680 Explore the library](https://lhlhai.github.io/prompt-library/)** · "
        "**[\U0001F4D6 Browse prompts](https://lhlhai.github.io/prompt-library/prompts.html)** · "
        "**[\U0001F91D Contribute](https://lhlhai.github.io/prompt-library/contribute.html)**\n")
    return "\n".join(lines)


MARKER_START = "<!-- PROMPT-LIBRARY:START \u2014 auto-generated by scripts/generate-readme-badges.py; do not edit inside the markers -->"
MARKER_END = "<!-- PROMPT-LIBRARY:END -->"
SECTION_END_MARKERS = ("## \U0001F40D Commit", "---\n\n## \U0001F40D")


def refresh_profile_template(section_md: str) -> bool:
    """Refresh the Prompt Library section inside assets/profile-README.md.

    Uses HTML-comment markers so regeneration is exact and idempotent:

        <!-- PROMPT-LIBRARY:START ... -->
        (generated section lives between the markers)
        <!-- PROMPT-LIBRARY:END -->

    If the file has no markers but does have a "## \U0001F40D Commit" heading,
    the section is inserted (with markers) right before it.
    """
    path = os.path.join(ASSETS_DIR, "profile-README.md")
    if not os.path.exists(path):
        return False
    content = open(path, encoding="utf-8").read()
    body = section_md.rstrip("\n")
    s_idx = content.find(MARKER_START)
    e_idx = content.find(MARKER_END)
    if s_idx != -1 and e_idx != -1 and e_idx > s_idx:
        s_line_end = content.index("\n", s_idx) + 1
        new_content = content[:s_line_end] + body + "\n\n" + content[e_idx:]
    else:
        snake_idx = content.find("## \U0001F40D Commit")
        if snake_idx == -1:
            return False
        block = MARKER_START + "\n" + body + "\n\n" + MARKER_END + "\n\n"
        new_content = content[:snake_idx] + block + content[snake_idx:]
    open(path, "w", encoding="utf-8").write(new_content)
    return True


def main() -> None:
    items = load_prompts()
    counts = Counter(i["label"] for i in items)
    total = len(items)
    words = sum(len(re.findall(r"\S+", i.get("prompt", ""))) for i in items)
    js_lines = len(open(PROMPTS_JS, encoding="utf-8").read().splitlines())
    stats = {
        "total": total,
        "categories": len(counts),
        "max_number": max(int(i["number"]) for i in items),
        "words": words,
        "js_lines": js_lines,
        "top_labels": counts.most_common(6),
    }

    os.makedirs(ASSETS_DIR, exist_ok=True)
    with open(os.path.join(ASSETS_DIR, "readme-banner.svg"), "w", encoding="utf-8") as f:
        f.write(build_banner(stats))
    with open(os.path.join(ASSETS_DIR, "prompt-map.svg"), "w", encoding="utf-8") as f:
        f.write(build_prompt_map(counts, total))
    with open(os.path.join(ASSETS_DIR, "README-BADGES.md"), "w", encoding="utf-8") as f:
        f.write("<!-- Paste this into your profile README (lhlhai/lhlhai) or this repo's README.\n"
                "     Replace <BRANCH> with your default branch (e.g. main).\n"
                "     Regenerated automatically by .github/workflows/readme-badges.yml -->\n\n")
        f.write(build_badge_md(stats, counts))

    section_md = build_section_md(stats, counts)
    with open(os.path.join(ASSETS_DIR, "PROMPT-LIBRARY-SECTION.md"), "w", encoding="utf-8") as f:
        f.write(section_md.rstrip("\n") + "\n\n---\n")

    refreshed = refresh_profile_template(section_md)

    print(f"OK: {total} prompts, {stats['categories']} categories, {words:,} words")
    print("Wrote assets/readme-banner.svg, assets/prompt-map.svg, assets/README-BADGES.md,"
          " assets/PROMPT-LIBRARY-SECTION.md"
          + (", assets/profile-README.md (section refreshed)" if refreshed else ""))


if __name__ == "__main__":
    main()
