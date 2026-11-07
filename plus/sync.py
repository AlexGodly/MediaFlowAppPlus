#!/usr/bin/env python3
"""One-way, fail-closed MediaFlowApp -> MediaFlowAppPlus mirror.

MediaFlowAppPlus is MediaFlowApp, unchanged, except for what makes it the
MediaFlow Plus app:
  * it signs in to the MediaFlow Plus Supabase project and opens the Plus website;
  * it is called "MediaFlow Plus" and uses its own app ids (Android/iOS
    com.alexgodly.plus.mediaflow, its own Windows installer id), so it installs
    next to MediaFlow instead of over it;
  * its release files are named MediaFlowPlus-<version>-... and its releases are
    tagged mediaflowappplus-v<version> (same version as MediaFlowApp).

Only --plus is written. The upstream checkout is read-only. Every patch expects
an exact layout and stops the sync (nothing is published) if MediaFlowApp
changed that layout, so a silent half-patched build can't reach users.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

PLUS_URL = "https://puaqaobplyrdrujapznp.supabase.co"
PLUS_KEY = "sb_publishable_nbfeKXdimfBv7lsbiJCBAw_54HIEr0G"
PLUS_WEBSITE = "https://alexgodly.github.io/MediaFlowPlus/"
PERSONAL_REF = "wgeijxfdpgehesxialxm"
PLUS_NAME = "MediaFlow Plus"
PLUS_EXE = "MediaFlowPlus.exe"  # Windows build targets can't contain spaces
PLUS_ORG = "com.alexgodly.plus"
PLUS_WINDOWS_APP_ID = "{{5D3A9E47-2B8C-4F61-A0D3-7E1C9B4F8A26}"

# Paths Plus owns. The mirror never deletes or overwrites them.
PLUS_OWNED = ("plus/", ".github/workflows/plus-sync.yml",
              ".github/workflows/plus-release.yml", "README.md", "CLAUDE.md")
# Upstream paths that are not mirrored.
SKIP = ("legacy/", "beta/", ".git/", ".github/workflows/release.yml",
        "README.md", "CLAUDE.md")
OVERLAY = Path("plus/overlay")
STATE = Path("plus/state.json")


def die(message: str) -> None:
    raise SystemExit("Plus sync blocked: " + message)


def owned(rel: str) -> bool:
    return any(rel == p or (p.endswith("/") and rel.startswith(p)) for p in PLUS_OWNED)


def skipped(rel: str) -> bool:
    return any(rel == p or (p.endswith("/") and rel.startswith(p)) for p in SKIP)


def files(root: Path) -> list[str]:
    out = []
    for f in root.rglob("*"):
        if f.is_file() or f.is_symlink():
            rel = f.relative_to(root).as_posix()
            if not rel.startswith(".git/"):
                out.append(rel)
    return sorted(out)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace(text: str, old: str, new: str, expected: int, where: str) -> str:
    found = text.count(old)
    if found != expected:
        die(f"{where}: expected {expected}x {old!r}, found {found} (MediaFlowApp layout changed; review needed)")
    return text.replace(old, new)


def resub(text: str, pattern: str, new: str, where: str) -> str:
    text, n = re.subn(pattern, lambda _m: new, text, count=1, flags=re.MULTILINE)
    if n != 1:
        die(f"{where}: pattern {pattern!r} not found (MediaFlowApp layout changed; review needed)")
    return text


def patch_config(t: str) -> str:
    if PERSONAL_REF not in t:
        die("lib/src/config.dart no longer points at the MediaFlow project; refusing to guess")
    t = resub(t, r"^const String kSupabaseUrl = '[^']*';$", f"const String kSupabaseUrl = '{PLUS_URL}';", "config.dart")
    t = resub(t, r"^const String kSupabasePublishableKey = '[^']*';$", f"const String kSupabasePublishableKey = '{PLUS_KEY}';", "config.dart")
    t = resub(t, r"^const String kWebsiteUrl = '[^']*';$", f"const String kWebsiteUrl = '{PLUS_WEBSITE}';", "config.dart")
    return t


def patch_prepare(t: str) -> str:
    where = "tool/prepare_platforms.py"
    t = replace(t, 'NAME = "MediaFlow"\n', f'NAME = "{PLUS_NAME}"\n', 1, where)
    t = replace(t, """f'set(BINARY_NAME "{NAME}")'""", """'set(BINARY_NAME "%s")' % NAME.replace(" ", "")""", 1, where)
    t = replace(t, """rf'\\1"{NAME}.exe"'""", """r'\\1"%s.exe"' % NAME.replace(" ", "")""", 1, where)
    return t


def patch_build(t: str) -> str:
    t = replace(t, "--org com.alexgodly ", f"--org {PLUS_ORG} ", 3, "build.yml")
    t = replace(t, "MediaFlow.exe", PLUS_EXE, t.count("MediaFlow.exe") or 1, "build.yml")
    t = replace(t, "MediaFlow-${{ inputs.app_version }}", "MediaFlowPlus-${{ inputs.app_version }}", 3, "build.yml")
    return t


def patch_installer(t: str) -> str:
    t = resub(t, r"^AppId=.*$", f"AppId={PLUS_WINDOWS_APP_ID}", "windows_installer.iss")
    t = resub(t, r"^AppName=MediaFlow$", f"AppName={PLUS_NAME}", "windows_installer.iss")
    t = resub(t, r"^DefaultDirName=\{autopf\}\\MediaFlow$", f"DefaultDirName={{autopf}}\\{PLUS_NAME}", "windows_installer.iss")
    t = resub(t, r"^DefaultGroupName=MediaFlow$", f"DefaultGroupName={PLUS_NAME}", "windows_installer.iss")
    t = resub(t, r"^OutputBaseFilename=MediaFlow-", "OutputBaseFilename=MediaFlowPlus-", "windows_installer.iss")
    t = replace(t, "MediaFlow.exe", PLUS_EXE, t.count("MediaFlow.exe") or 1, "windows_installer.iss")
    t = t.replace('"{group}\\MediaFlow"', f'"{{group}}\\{PLUS_NAME}"')
    t = t.replace('"{autodesktop}\\MediaFlow"', f'"{{autodesktop}}\\{PLUS_NAME}"')
    t = t.replace('"Open MediaFlow"', f'"Open {PLUS_NAME}"')
    return t


PATCHES = {
    "lib/src/config.dart": patch_config,
    "tool/prepare_platforms.py": patch_prepare,
    ".github/workflows/build.yml": patch_build,
    "tool/windows_installer.iss": patch_installer,
}


def sync(upstream: Path, plus: Path, commit: str) -> None:
    upstream, plus = upstream.resolve(), plus.resolve()
    if upstream == plus or upstream in plus.parents or plus in upstream.parents:
        die("upstream and Plus must be separate checkouts")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        die("expected a full MediaFlowApp commit SHA")

    src = [f for f in files(upstream) if not skipped(f)]
    for rel in src:
        if owned(rel):
            die("MediaFlowApp now has a file at a Plus-owned path: " + rel)
    for rel in PATCHES:
        if rel not in src:
            die("MediaFlowApp no longer has " + rel)
    for rel in files(plus / OVERLAY):
        if rel not in src:
            die("Plus overlay replaces a file MediaFlowApp no longer has: " + rel)

    # Mirror: remove everything not Plus-owned, then copy upstream.
    for rel in files(plus):
        if not owned(rel):
            (plus / rel).unlink()
    for d in sorted((p for p in plus.rglob("*") if p.is_dir() and ".git" not in p.parts), reverse=True):
        if not any(d.iterdir()):
            d.rmdir()
    for rel in src:
        dest = plus / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(upstream / rel, dest)

    for rel, fn in PATCHES.items():
        p = plus / rel
        p.write_text(fn(p.read_text(encoding="utf-8")), encoding="utf-8")
    overlay = files(plus / OVERLAY)
    for rel in overlay:
        shutil.copy2(plus / OVERLAY / rel, plus / rel)

    # Every other file must be byte-identical to MediaFlowApp.
    changed = set(PATCHES) | set(overlay)
    for rel in src:
        if rel not in changed and sha(upstream / rel) != sha(plus / rel):
            die("unexpected difference in " + rel)
    for rel in ("lib", "tool", ".github"):
        for f in (plus / rel).rglob("*"):
            if f.is_file() and PERSONAL_REF in f.read_text(encoding="utf-8", errors="ignore"):
                die("MediaFlow (Personal) Supabase project still referenced in " + f.relative_to(plus).as_posix())

    version = re.search(r"^version:\s*(\d+\.\d+\.\d+)\+\d+\s*$", (plus / "pubspec.yaml").read_text(), re.M)
    if not version:
        die("pubspec.yaml version not found")
    (plus / STATE).write_text(json.dumps({
        "upstream_repo": "AlexGodly/MediaFlowApp",
        "upstream_sha": commit,
        "app_version": version.group(1),
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Mirrored {len(src)} MediaFlowApp files ({len(src) - len(changed)} identical, "
          f"{len(changed)} Plus-patched) at {commit[:12]}, version {version.group(1)}.")


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    cli.add_argument("--upstream", type=Path, required=True)
    cli.add_argument("--plus", type=Path, required=True)
    cli.add_argument("--sha", required=True)
    a = cli.parse_args()
    sync(a.upstream, a.plus, a.sha)
