#!/usr/bin/env python3
"""Apply full NALAR branding (official logo PNG, wordmarks, favicon, PWA manifest, UI text)."""

import glob
import json
import os
import re
import shutil

CLIENT_DIR = "/opt/nalar/client"
LOGO_SRC = "/opt/nalar/assets/nalar-logo.png"


def install_logo_assets():
    if not os.path.exists(LOGO_SRC):
        raise FileNotFoundError(f"Official NALAR logo not found at {LOGO_SRC}")

    targets = [
        "nalar-logo.png",
        "apple-touch-icon.png",
        "icon-192x192.png",
        "icon-512x512.png",
        "favicon-32x32.png",
        "favicon-16x16.png",
        "favicon.ico",
    ]
    for name in targets:
        shutil.copyfile(LOGO_SRC, os.path.join(CLIENT_DIR, name))
    print(f"[brand] Installed official NALAR logo across {len(targets)} icon files")


def patch_index_html():
    path = os.path.join(CLIENT_DIR, "index.html")
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    html = re.sub(r"<title>[^<]*</title>", "<title>NALAR — AI Coding Harness</title>", html)
    html = html.replace("T3 Code", "NALAR")
    html = html.replace(
        '<link rel="icon" href="/favicon.ico" sizes="48x48" />',
        '<link rel="icon" type="image/png" href="/nalar-logo.png" />',
    )
    html = html.replace(
        '<img id="boot-shell-logo" src="/apple-touch-icon.png" alt="NALAR" />',
        '<img id="boot-shell-logo" src="/nalar-logo.png" alt="NALAR" />',
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
        {"src": "/nalar-logo.png", "sizes": "500x500", "type": "image/png", "purpose": "any"},
        {"src": "/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"},
        {"src": "/icon-192x192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "/icon-512x512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
    ]

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[brand] Patched {path}")


def patch_js_assets():
    patched_files = 0
    for path in sorted(glob.glob(os.path.join(CLIENT_DIR, "assets", "*.js"))):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            src = f.read()

        updated = src

        # 1. Replace main header T3 SVG + "Code" wordmark with larger (+70%) official green NALAR logo + "NALAR"
        updated = re.sub(
            r'\(0,Z\.jsx\)\(yv,\{"aria-label":`T3`,className:`h-\[1cap\] w-auto shrink-0`\}\)',
            '(0,Z.jsx)(`img`,{src:`/nalar-logo.png`,alt:`NALAR`,className:`h-7 w-7 shrink-0 object-contain`})',
            updated,
        )
        updated = updated.replace(
            'src:`/nalar-logo.png`,alt:`NALAR`,className:`h-4 w-4 shrink-0 object-contain`',
            'src:`/nalar-logo.png`,alt:`NALAR`,className:`h-7 w-7 shrink-0 object-contain`',
        )
        updated = updated.replace(
            'className:`inline-flex min-w-0 items-baseline gap-1 text-sm font-medium tracking-tight`,children:[r,(0,Z.jsx)(`span`,{className:a,children:`Code`})]',
            'className:`inline-flex min-w-0 items-center gap-2 text-2xl font-semibold tracking-tight`,children:[r,(0,Z.jsx)(`span`,{className:a,children:`NALAR`})]',
        )
        updated = updated.replace(
            'className:`inline-flex min-w-0 items-center gap-1.5 text-sm font-semibold tracking-tight`,children:[r,(0,Z.jsx)(`span`,{className:a,children:`NALAR`})]',
            'className:`inline-flex min-w-0 items-center gap-2 text-2xl font-semibold tracking-tight`,children:[r,(0,Z.jsx)(`span`,{className:a,children:`NALAR`})]',
        )
        updated = re.sub(
            r'(ml-\[var\(--workspace-titlebar-content-left\)\] hidden )h-7( w-fit min-w-0 shrink-0 items-center overflow-hidden rounded-md outline-hidden ring-ring focus-visible:ring-2 focus-visible:ring-inset md:flex`,r\),t\[0\]=r,t\[1\]=i\);let a;t\[2\]===n\?a=t\[3\]:\(a=\(0,Z\.jsx\)\(hB,\{onBackdrop:n\}\))',
            r'\1h-9\2',
            updated,
        )
        # Also handle fresh (unpatched) T3 bundle where NALAR home was still T3 home before step 3
        updated = updated.replace(
            'ml-[var(--workspace-titlebar-content-left)] hidden h-7 w-fit min-w-0 shrink-0 items-center overflow-hidden rounded-md outline-hidden ring-ring focus-visible:ring-2 focus-visible:ring-inset md:flex',
            'ml-[var(--workspace-titlebar-content-left)] hidden h-9 w-fit min-w-0 shrink-0 items-center overflow-hidden rounded-md outline-hidden ring-ring focus-visible:ring-2 focus-visible:ring-inset md:flex',
        )

        # 2. Replace standalone (/pair) T3 SVG + "Code" wordmark with official green NALAR logo + "NALAR"
        updated = re.sub(
            r'className:`flex items-baseline gap-1\.5`,role:`img`,"aria-label":`T3 Code`,children:\[\(0,i\.jsx\)\(a,\{[^}]+\}\),\(0,i\.jsx\)\(`span`,\{className:`text-lg font-medium tracking-tight`,children:`Code`\}\)\]',
            'className:`flex items-center gap-2.5`,role:`img`,"aria-label":`NALAR`,children:[(0,i.jsx)(`img`,{src:`/nalar-logo.png`,alt:`NALAR`,className:`h-8 w-8 shrink-0 object-contain`}),(0,i.jsx)(`span`,{className:`text-2xl font-semibold tracking-tight text-foreground`,children:`NALAR`})]',
            updated,
        )
        updated = updated.replace(
            'className:`flex items-center gap-2`,role:`img`,"aria-label":`NALAR`,children:[(0,i.jsx)(`img`,{src:`/nalar-logo.png`,alt:`NALAR`,className:`h-6 w-6 shrink-0 object-contain`}),(0,i.jsx)(`span`,{className:`text-lg font-semibold tracking-tight text-foreground`,children:`NALAR`})]',
            'className:`flex items-center gap-2.5`,role:`img`,"aria-label":`NALAR`,children:[(0,i.jsx)(`img`,{src:`/nalar-logo.png`,alt:`NALAR`,className:`h-8 w-8 shrink-0 object-contain`}),(0,i.jsx)(`span`,{className:`text-2xl font-semibold tracking-tight text-foreground`,children:`NALAR`})]',
        )

        # 3. Replace any remaining aria-label:`T3` and all visible "T3 Code" display strings -> "NALAR"
        updated = updated.replace('"aria-label":`T3`', '"aria-label":`NALAR`')
        updated = updated.replace("T3 Code", "NALAR")

        if updated != src:
            with open(path, "w", encoding="utf-8") as f:
                f.write(updated)
            patched_files += 1

    print(f"[brand] Patched {patched_files} JS asset files with official NALAR logo & branding")


if __name__ == "__main__":
    install_logo_assets()
    patch_index_html()
    patch_manifest()
    patch_js_assets()
    print("[brand] Official NALAR rebranding complete.")
