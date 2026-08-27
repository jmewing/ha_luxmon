# Releasing

The integration version lives in `custom_components/luxmon/manifest.json`
(`"version"` field). It is **coupled** to the add-on version in the
[ha_luxmon_addons](https://github.com/jmewing/ha_luxmon_addons) repo — the
add-on's `run.sh` downloads this repo's release zip at `v${VERSION}`.

## Automatic release (default)

`.github/workflows/release.yml` runs on every push to `main`:

1. Determines the next semantic version from commit subjects
   (Conventional Commits — see `scripts/bump-version.sh`).
2. Bumps `manifest.json`, commits, and tags `vX.Y.Z`.
3. Builds `luxmon.zip` via `scripts/release.sh`.
4. Creates a GitHub release with the zip attached.
5. Fires a `repository_dispatch` event to `ha_luxmon_addons` so the add-on
   version syncs automatically.

### Bump rules

| Commit subject | Bump |
| -------------- | ---- |
| `feat(inverter): ...` | MAJOR (new inverter support) |
| `feat: ...` / `feat(scope): ...` | MINOR (new feature) |
| `fix:` / `chore:` / `docs:` / `refactor:` / `perf:` / `test:` / `ci:` | PATCH |
| `BREAKING CHANGE` / trailing `!` | MAJOR |

### Required secret

Set a **`ADDON_REPO_TOKEN`** secret (GitHub PAT with `repo` scope on
`jmewing/ha_luxmon_addons`) so the release workflow can notify the add-on repo.

## Manual release (fallback)

```bash
# 1. Bump the version
scripts/bump-version.sh --write

# 2. Build the zip
scripts/release.sh

# 3. Commit, tag, and push
git add custom_components/luxmon/manifest.json
git commit -m "chore: bump version to X.Y.Z"
git tag vX.Y.Z
git push origin main --tags
```

Then attach `custom_components/luxmon.zip` to the GitHub release for `vX.Y.Z`.
