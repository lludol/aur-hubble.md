# Maintainer memo

Notes for updating the AUR packages manually or configuring automation.

This repo hosts two AUR packages:

- **hubble.md** — source build, runs against the system Electron.
- **hubble.md-bin** — repackages the upstream per-arch `.deb` release.

Both track upstream's `desktop-v<version>` release tags on
[bholmesdev/hubble.md](https://github.com/bholmesdev/hubble.md/releases).

## GitHub Action

The workflow in `.github/workflows/aur.yml` keeps both PKGBUILDs in sync:

- **Schedule:** runs daily at 03:00 UTC.
- **Manual:** Actions → Auto Update AUR Packages → Run workflow.
- **Test locally (no AUR push):** `act workflow_dispatch`
- Fetches the [latest Hubble desktop release](https://github.com/bholmesdev/hubble.md/releases/latest),
  strips the `desktop-v` prefix to get `pkgver`, updates both PKGBUILDs, runs
  `updpkgsums`, regenerates each `.SRCINFO`, commits, then pushes each package to its AUR repo.
- Only commits/pushes when a new version is detected.
- `namcap: false` — the source package builds a large pnpm/Electron tree, so we
  skip the action's in-container build/lint and only refresh sums + `.SRCINFO`.

## AUR account and SSH key

1. Create an account on [aur.archlinux.org](https://aur.archlinux.org).
2. In [AUR Account Settings](https://aur.archlinux.org/account/) → **SSH Public Key**, add your public key (e.g. `~/.ssh/ed25519.pub`).

## GitHub secrets and variables

In this repo: **Settings → Secrets and variables → Actions**.

### Secret

| Name | Value |
|------|-------|
| `AUR_SSH_KEY` | Your AUR **private** key (full PEM, including `-----BEGIN ... -----` and `-----END ... -----`) |

Without `AUR_SSH_KEY`, the workflow still updates this repo but skips pushing to the AUR.

### Variables (Actions → Variables tab)

| Name | Value |
|------|-------|
| `AUR_USERNAME` | Your AUR username |
| `AUR_EMAIL` | The email tied to your AUR account |

These are used as the git author when pushing to AUR (the AUR requires commits to come from a registered account).

## First push to AUR

The workflow cannot create a new AUR package. You must do the initial push for
each package manually:

```bash
# hubble.md (source)
git -c init.defaultBranch=master clone ssh://aur@aur.archlinux.org/hubble.md.git /tmp/aur-hubble
cp hubble.md/PKGBUILD hubble.md/.SRCINFO LICENSE /tmp/aur-hubble/
cd /tmp/aur-hubble
git config user.name "your-aur-username"
git config user.email "your-aur-email"
git add PKGBUILD .SRCINFO LICENSE
git commit -m "Initial import: hubble.md 0.1.14"
git push

# hubble.md-bin (binary)
git -c init.defaultBranch=master clone ssh://aur@aur.archlinux.org/hubble.md-bin.git /tmp/aur-hubble-bin
cp hubble.md-bin/PKGBUILD hubble.md-bin/.SRCINFO LICENSE /tmp/aur-hubble-bin/
cd /tmp/aur-hubble-bin
git config user.name "your-aur-username"
git config user.email "your-aur-email"
git add PKGBUILD .SRCINFO LICENSE
git commit -m "Initial import: hubble.md-bin 0.1.14"
git push
```

After this, the GitHub Action handles all future updates.

## Manual AUR update

If you need to push to the AUR by hand after the initial import (per package):

```bash
cd hubble.md            # or: cd hubble.md-bin
# After editing PKGBUILD: updpkgsums && makepkg --printsrcinfo > .SRCINFO
```

Then commit and push to the matching `ssh://aur@aur.archlinux.org/<pkgname>.git`.

## Bumping versions by hand

1. Set `pkgver` to the new desktop version in both PKGBUILDs, reset `pkgrel=1`.
2. `updpkgsums` in each dir (refreshes `sha256sums` from the new release).
3. `makepkg --printsrcinfo > .SRCINFO` in each dir.
4. Commit + push.

## Notes / gotchas

- **`git init` in `prepare()` is mandatory (Tailwind v4):** the source build runs
  `git init && git add -A` before building, and `git` is a makedepend. Tailwind
  v4 (`@tailwindcss/oxide`) decides which files to scan for utility classes by
  enumerating the **git working tree** (the packages use the v4 `@source "."`
  directive). The GitHub release tarball ships no `.git`, so without this the
  scan finds nothing: the app compiles cleanly but ships an almost-empty
  stylesheet (renderer CSS ~35 KB instead of ~93 KB) and renders **unstyled /
  broken**. With the git tree, the renderer CSS is byte-identical to upstream's
  official `.deb` (`index-CxdEtIUN.css`, 92.9 KB). Symptom if it regresses:
  layout looks broken while `hubble.md-bin` (prebuilt) looks fine. **Do not
  remove the `prepare()`.**
- **Tag prefix:** upstream tags are `desktop-v<version>`; `pkgver` is the bare
  version. The source PKGBUILD reconstructs the tag as `desktop-v$pkgver`, and
  the archive extracts to `hubble.md-desktop-v$pkgver`.
- **hubble.md source deps:** the build assembles a minimal runtime
  `node_modules` with only the prod deps the main process still needs at
  runtime (`electron-updater`, `ignore`, `zod`). If a future release adds a new
  externalized main-process dependency, add it to the `pick=[...]` list in
  `build()`.
- **hubble.md-bin license:** the `.deb` payload has no MIT `LICENSE`, so the
  PKGBUILD pulls it from the tagged source as a separate pinned source. The
  per-arch `.deb` checksums (`sha256sums_x86_64` / `sha256sums_aarch64`) must
  both be refreshed on every bump — `updpkgsums` handles all source arrays.
- **chrome-sandbox:** Arch enables unprivileged user namespaces, so the bundled
  `chrome-sandbox` is shipped non-SUID (`0755`); no `chmod 4755` postinstall.
- **`Unsupported engine` build warning:** during `pnpm install` you may see
  `[WARN] Unsupported engine: wanted: {"node":"22.x"}`. This is cosmetic. It
  comes from `apps/web`, which is *not* built here — the PKGBUILD only builds
  `@hubble.md/desktop...`, and the desktop package declares no engine
  constraint. pnpm validates engines across the whole workspace during install,
  so the warning fires whenever the build host's Node is newer than 22.x. Safe
  to ignore; it has no effect on the packaged output. (Can't be silenced by
  pinning Node — `nodejs-lts-jod` would conflict with the rolling `nodejs`
  makedepend.)
- **`ERR_PNPM_IGNORED_BUILDS` note:** pnpm 10+ prints "Ignored build scripts:
  esbuild, sharp, msw, …" during install. Also harmless — those are web/installer
  dependencies, not part of the desktop runtime, and esbuild ships its binary via
  platform optional-deps rather than a postinstall.
