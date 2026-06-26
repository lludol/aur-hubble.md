# AUR packages for Hubble.md

Arch User Repository (AUR) packages for [Hubble.md](https://github.com/bholmesdev/hubble.md) — the free, open-source Markdown notepad for you and your agents.

## Packages

| Package | Description | AUR |
|---------|-------------|-----|
| **hubble.md** | Source build — compiles the desktop app and runs against the system Electron (`electron42`) | [hubble.md](https://aur.archlinux.org/packages/hubble.md) |
| **hubble.md-bin** | Prebuilt binary — repackages the upstream `.deb` release (bundled Electron) | [hubble.md-bin](https://aur.archlinux.org/packages/hubble.md-bin) |

The two packages conflict (both ship `/usr/bin/hubble.md`); install one. Pick **hubble.md-bin** for a fast install, **hubble.md** if you prefer building from source against the distro Electron.

## Install

Using an AUR helper (e.g. [yay](https://github.com/Jguer/yay)):

```bash
yay -S hubble.md-bin   # prebuilt binary (fast)
# or
yay -S hubble.md       # build from source
```

Manual build from this repo:

```bash
cd hubble.md-bin       # or: cd hubble.md
makepkg -si
```

## Usage

After install, the `hubble.md` binary is in your `PATH`:

```bash
hubble.md
# open a file or folder
hubble.md ~/notes
```

Hubble also registers a desktop entry (Markdown Editor) and `.md` file association.

## License

The PKGBUILDs and this repo are licensed under [0BSD](LICENSE). Hubble.md itself is [MIT](https://github.com/bholmesdev/hubble.md/blob/main/LICENSE)-licensed.

The PKGBUILDs are automatically updated via GitHub Actions — see [MAINTAINER.md](MAINTAINER.md).
