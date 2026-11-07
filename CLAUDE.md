# MediaFlowAppPlus — working rules

This repo is a generated mirror of `AlexGodly/MediaFlowApp` for the MediaFlow Plus backend (owner's decision, 2026-11-07: "always identical").

- **Don't change app code here.** Make the change in MediaFlowApp (following its CLAUDE.md); `plus-sync.yml` brings it here within 15 minutes and `plus-release.yml` publishes `mediaflowappplus-v<version>`. Edits outside the Plus-owned files are overwritten on the next sync.
- Plus-owned files: `plus/` (sync script, state, overlays), `.github/workflows/plus-sync.yml`, `.github/workflows/plus-release.yml`, `README.md`, this file.
- The only differences from MediaFlowApp are in `plus/sync.py` (`PATCHES`) and `plus/overlay/`. If a sync fails with "layout changed; review needed", update the matching patch in `plus/sync.py`, then run the sync workflow by hand.
- Backend: Supabase project `puaqaobplyrdrujapznp` (MediaFlow Plus). Never point this app at `wgeijxfdpgehesxialxm`. No schema/policy changes without the owner's explicit approval.
