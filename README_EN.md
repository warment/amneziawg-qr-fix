# AmneziaWG QR Fix

_Recover a working QR for AmneziaWG from a broken export_

### [Русский](README.md) | [English](README_EN.md)

A tool that recovers an AmneziaWG config from a `vpn://...` / `.vpn` export into a plain text `[Interface]` + `[Peer]` config and builds a QR from it that the AmneziaWG client actually imports.

> [!NOTE]
> This is a **standalone Python command-line program** (`scripts/decode_amnezia_vpn.py`). No AI is required to use it. The `SKILL.md` and `agents/openai.yaml` files are an optional wrapper for AI agents (Claude, Codex, OpenAI) so an assistant can invoke the script on your behalf. If you don't use an AI agent, ignore those files.

> [!TIP]
> The problem is documented in official issues: [amneziawg-android#56](https://github.com/amnezia-vpn/amneziawg-android/issues/56), [amnezia-client#2119](https://github.com/amnezia-vpn/amnezia-client/issues/2119). Amnezia itself acknowledges: _"The QR code cannot be scanned if you selected AmneziaWG native format"_.

## Installation

Requires Python 3.10+. For PNG generation install `qrcode[pil]`:

```
$ pip install "qrcode[pil]"
```

## Usage

Quick start — a QR for a phone:

```
$ python3 scripts/decode_amnezia_vpn.py export.vpn -o fixed.conf --png qr.png --mtu 1280
```

After that:

- `fixed.conf` — a working config for AmneziaWG / WireGuard;
- `qr.png` — a QR the AmneziaWG client imports.

## How it works

1. Reads a `.vpn` file or a raw `vpn://...` string.
2. Strips `vpn://`, base64url-decodes, zlib-decompresses the blob (with or without the 4-byte header).
3. Finds the hidden config and verifies it is `[Interface]` + `[Peer]`.
4. On decode failure, tries to repair a single corrupted base64url character.
5. Fixes unresolved placeholders `$PRIMARY_DNS` / `$SECONDARY_DNS` (default `1.1.1.1, 8.8.8.8`, override via `--dns`).
6. Inserts/replaces `MTU` in `[Interface]` (`--mtu 1280`) — without it web traffic dies on mobile networks.
7. Writes `.conf` and, optionally, generates a QR PNG from the text, not from `vpn://`.

## Options

| Flag | Purpose |
|------|---------|
| `source` | path to `.vpn` or a `vpn://...` string |
| `-o, --output-conf` | where to write `.conf` (stdout otherwise) |
| `--png` | write a QR PNG |
| `--dns "a, b"` | replace `$PRIMARY_DNS/$SECONDARY_DNS` (default `1.1.1.1, 8.8.8.8`) |
| `--mtu 1280` | insert/replace `MTU` in `[Interface]` |
| `--no-repair` | do not repair a corrupted base64url character |
| `--raw` | do not fix placeholders and MTU, return as-is |

> [!TIP]
> For import, prefer copying `fixed.conf` into the AmneziaWG client (**Import from file**). Scanning `qr.png` is the alternative.

> [!IMPORTANT]
> Configs with unresolved `$UPPERCASE_VARS` are rejected unless fixed. The QR is built only from valid text with `[Interface]` and `[Peer]` — never from `vpn://` or JSON.

## Examples

```
# Substitute your own DNS
$ python3 scripts/decode_amnezia_vpn.py export.vpn -o fixed.conf --dns "9.9.9.9, 149.112.112.112"

# Return the config unmodified
$ python3 scripts/decode_amnezia_vpn.py export.vpn --raw
```

## License

Licensed under the MIT License (see [LICENSE](LICENSE)).
