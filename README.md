# Notion Flatpak

Unofficial Flatpak packaging of [Notion](https://www.notion.so) — your connected workspace for wiki, docs & projects.

## Install from BlossomOS

The easiest way to install Notion is from the BlossomOS Flatpak repository:

```bash
curl -fsSL https://repo.blossomos.org/BLOSSOMOS-GPG-KEY.pub -o /tmp/flatpak-repo-key.asc \
  && flatpak remote-add --if-not-exists --gpg-import=/tmp/flatpak-repo-key.asc blossomos https://repo.blossomos.org/flatpak
flatpak install blossomos so.notion.Notion
```

Then launch with:

```bash
flatpak run so.notion.Notion
```

## Build from source

### Requirements

- `flatpak-builder`
- `org.freedesktop.Platform` and `org.freedesktop.Sdk` (version 24.08) — installed automatically via `--install-deps-from=flathub`

### Build and install locally

```bash
flatpak-builder --install-deps-from=flathub --force-clean --install --user build-dir so.notion.Notion.yml
```

### Build a distributable `.flatpak` bundle

```bash
flatpak-builder --install-deps-from=flathub --force-clean --repo=repo build-dir so.notion.Notion.yml
flatpak build-bundle repo notion.flatpak so.notion.Notion
```

The resulting `notion.flatpak` can be installed on any machine with:

```bash
flatpak install notion.flatpak
```

## Runtime flags

You can pass extra Electron flags by creating `~/.config/notion-flags.conf` (one flag per line, lines starting with `#` are ignored).

## Notes

- Auto-updates are disabled — update by rebuilding or pulling a new version from the BlossomOS repo.
- The Electron sandbox is intentionally disabled (`--no-sandbox`) because the Flatpak sandbox provides equivalent isolation.
- Notion stores its data in `~/.config/Notion`.
