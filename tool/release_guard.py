"""MediaFlowAppPlus release contract (replaces MediaFlowApp's guard in the mirror).

Same version rules as MediaFlowApp, plus: the app must point at the MediaFlow Plus
Supabase project, never at MediaFlow's, and must build as its own app
(com.alexgodly.plus.mediaflow, MediaFlowPlus-* files). Plus has no legacy/ source archive;
each release attaches a source zip made from the release commit instead."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
pubspec = (ROOT / "pubspec.yaml").read_text(encoding="utf-8")
config = (ROOT / "lib/src/config.dart").read_text(encoding="utf-8")
prepare = (ROOT / "tool/prepare_platforms.py").read_text(encoding="utf-8")
release = (ROOT / ".github/workflows/plus-release.yml").read_text(encoding="utf-8")

m = re.search(r"^version:\s*(\d+\.\d+\.\d+)\+(\d+)\s*$", pubspec, re.MULTILINE)
if not m:
    sys.exit("pubspec.yaml version must be X.Y.Z+<build number>")
app_version = m.group(1)

personal_ref = "wgeijxfdpg" + "ehesxialxm"  # split so the leak check in plus/sync.py stays meaningful
checks = {
    "in-app label": f"kAppVersionLabel = '{app_version}'" in config,
    "Plus Supabase": "kSupabaseUrl = 'https://puaqaobplyrdrujapznp.supabase.co'" in config,
    "Plus website": "kWebsiteUrl = 'https://alexgodly.github.io/MediaFlowPlus/'" in config,
    "no MediaFlow (Personal) project in lib/": not any(
        personal_ref in f.read_text(encoding="utf-8", errors="ignore") for f in (ROOT / "lib").rglob("*.dart")),
    "MediaFlowApp release notes": (ROOT / f"docs/releases/mediaflowapp-v{app_version}.md").is_file(),
    "Plus app name and id": 'NAME = "MediaFlow Plus"' in prepare and "plus_app_ids(platforms)" in prepare
        and "com.alexgodly.plus.mediaflow" in prepare,
    "builds with MediaFlowApp's three-platform build": "uses: AlexGodly/MediaFlowApp/.github/workflows/build.yml@" in release,
    "stable release (not a pre-release)": "--prerelease" not in release and "--latest" in release,
}
for name in ("-Android.apk", "-Windows-x64-Setup.exe", "-Windows-x64-portable.zip", "-iOS-unsigned.ipa"):
    checks[f"release asset MediaFlowPlus-*{name}"] = f"MediaFlowPlus-${{APP_VERSION}}{name}" in release
failed = [k for k, ok in checks.items() if not ok]
if failed:
    sys.exit("Plus release contract failed: " + ", ".join(failed))
print(f"Plus release contract verified: mediaflowappplus-v{app_version} (stable; Android, Windows, iOS; Plus Supabase)")
