#!/usr/bin/env python3
"""Apply clean NALAR branding to the prebuilt web client assets in /opt/nalar/client."""

import glob
import json
import os
import re

CLIENT_DIR = "/opt/nalar/client"

# Sleek geometric "N" monogram SVG for favicon, splash screen & PWA icon
NALAR_ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128">
  <rect width="128" height="128" rx="28" fill="#0d0d0f"/>
  <rect x="4" y="4" width="120" height="120" rx="24" fill="none" stroke="#ffffff" stroke-opacity="0.14" stroke-width="2"/>
  <path d="M34 94V34H47.5L80.5 76.5V34H94V94H81L47.5 50.8V94H34Z" fill="#ffffff"/>
  <circle cx="94" cy="34" r="6" fill="#60a5fa"/>
</svg>
"""

# Inline monochrome geometric "N" glyph (fill=currentColor) replacing the hardcoded T3 SVG path
T3_PATH_PREFIX = "M33.4509 93V47.56H15.5309V37H64.3309"
NALAR_GLYPH_PATH = "M16 93V37H31L74 79V37H90V93H75L32 51V93H16Z"
T3_VIEWBOX = "15.5309 37 94.3941 56.96"
NALAR_VIEWBOX = "14 35 78 60"


def write_icon():
    icon_path = os.path.join(CLIENT_DIR, "nalar-icon.svg")
    with open(icon_path, "w", encoding="utf-8") as f:
        f.write(NALAR_ICON_SVG)
    print(f"[brand] Wrote {icon_path}")


def patch_index_html():
    path = os.path.join(CLIENT_DIR, "index.html")
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    html = re.sub(r"<title>[^<]*</title>", "<title>NALAR — AI Coding Harness</title>", html)
    html = html.replace("T3 Code", "NALAR")
    html = html.replace(
        '<link rel="icon" href="/favicon.ico" sizes="48x48" />',
        '<link rel="icon" type="image/svg+xml" href="/nalar-icon.svg" />',
    )
    html = html.replace(
        '<img id="boot-shell-logo" src="/apple-touch-icon.png" alt="NALAR" />',
        '<img id="boot-shell-logo" src="/nalar-icon.svg" alt="NALAR" />',
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[brand] Patched {path}")


def patch_manifest():
    path = os.path.join(CLIENT_DIR, "manifest.webmanifest")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["name"] = "NALAR"
    data["short_name"] = "NALAR"
    data["description"] = "NALAR AI Coding Harness"
    data["icons"] = [
        {"src": "/nalar-icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any"}
    ] + data.get("icons", [])

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[brand] Patched {path}")


def patch_js_assets():
    patched_files = 0
    for path in sorted(glob.glob(os.path.join(CLIENT_DIR, "assets", "*.js"))):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            src = f.read()

        updated = src

        # 1. Replace hardcoded T3 monogram SVG path & viewBox with NALAR geometric N mark
        if T3_PATH_PREFIX in updated:
            updated = re.sub(
                r"M33\.4509 93V47\.56H15\.5309[^`\"']+",
                NALAR_GLYPH_PATH,
                updated,
            )
            updated = updated.replace(T3_VIEWBOX, NALAR_VIEWBOX)

        # 2. Replace the split brand wordmark ("T3" SVG + "Code" span) -> ([N mark] + "NALAR")
        updated = updated.replace(
            'children:[r,(0,Z.jsx)(`span`,{className:a,children:`Code`})]',
            'children:[r,(0,Z.jsx)(`span`,{className:a,children:`NALAR`})]',
        )
        updated = re.sub(
            r'role:`img`,"aria-label":`T3 Code`,children:\[(.*?children:)`Code`',
            r'role:`img`,"aria-label":`NALAR`,children:[\1`NALAR`',
            updated,
        )

        # 3. Replace aria-label:`T3` and all visible "T3 Code" display strings -> "NALAR"
        updated = updated.replace('"aria-label":`T3`', '"aria-label":`NALAR`')
        updated = updated.replace("T3 Code", "NALAR")

        if updated != src:
            with open(path, "w", encoding="utf-8") as f:
                f.write(updated)
            patched_files += 1

    print(f"[brand] Patched {patched_files} JS asset files with NALAR branding")


if __name__ == "__main__":
    write_icon()
    patch_index_html()
    patch_manifest()
    patch_js_assets()
    print("[brand] NALAR rebranding complete.")
