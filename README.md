# MediaFlow Plus — native app (Android, Windows, iOS)

The [MediaFlowApp](https://github.com/AlexGodly/MediaFlowApp) native app for your **MediaFlow Plus** account: same app, same features, signed in to the [MediaFlow Plus website](https://alexgodly.github.io/MediaFlowPlus/)'s backend. Logs you make here appear on MediaFlow Plus and vice versa.

Download from [Releases](https://github.com/AlexGodly/MediaFlowAppPlus/releases).

| Platform | Release file |
| :-- | :-- |
| Android | `MediaFlowPlus-<version>-Android.apk` |
| Windows 10/11 x64 | `…-Windows-x64-Setup.exe` or `…-Windows-x64-portable.zip` |
| iPhone / iPad | `…-iOS-unsigned.ipa` (re-sign to install) |

It's a separate app (Android/iOS id `com.alexgodly.plus.mediaflow`, its own Windows installer), so it installs next to MediaFlow rather than replacing it.

## How it stays identical to MediaFlowApp

Nothing is developed here. Every 15 minutes `.github/workflows/plus-sync.yml` checks MediaFlowApp's `main`; when it moved, it copies every file (except MediaFlowApp's `legacy/` archives, release workflow, README and CLAUDE.md), then `plus/sync.py` changes only:

- `lib/src/config.dart` — MediaFlow Plus Supabase project, publishable key and website
- `tool/prepare_platforms.py`, `tool/windows_installer.iss`, `.github/workflows/build.yml` — the name "MediaFlow Plus", its own app ids and `MediaFlowPlus-*` file names
- `tool/release_guard.py` — replaced by `plus/overlay/tool/release_guard.py`

Every other file is checked to be byte-identical. If MediaFlowApp changes one of those spots so the patch no longer fits, the sync stops before anything is published.

After committing, it starts `.github/workflows/plus-release.yml`, which runs MediaFlowApp's own tests and three-platform build and publishes a stable release `mediaflowappplus-v<version>` whenever MediaFlowApp's version is new. `plus/state.json` records which MediaFlowApp commit is mirrored. Run the sync by hand from the Actions tab (**Mirror MediaFlowApp into MediaFlowAppPlus → Run workflow**).
