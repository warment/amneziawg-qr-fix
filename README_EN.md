# AmneziaWG QR Fix

### _Recover a working QR for AmneziaWG_

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Version 1.2.0](https://img.shields.io/badge/version-1.2.0-green.svg)](https://github.com/warment/amneziawg-qr-fix/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

### [English](https://github.com/warment/amneziawg-qr-fix) | [Русский](README.md)

[AmneziaWG](https://docs.amnezia.org/documentation/amnezia-wg/) is an obfuscated protocol on top of WireGuard. The AmneziaVPN app exports the config as a QR in `vpn://...` format, but the AmneziaWG client rejects that QR — a known bug that Amnezia itself acknowledges in its docs.

**QR Fix** unpacks `vpn://...` back into a plain text config `[Interface]` + `[Peer]` and builds a QR from it that the client actually imports.

> **What is this, exactly?**
> This is a **standalone Python command-line program** — `scripts/decode_amnezia_vpn.py`. Run it in your terminal, get a `.conf` and a QR. No AI required to use it.
> The `SKILL.md` and `agents/openai.yaml` files are an **optional wrapper for AI agents** (Claude, Codex, OpenAI, etc.): they let an assistant invoke the script on your behalf. If you don't use an AI agent, ignore those files — they don't affect how the program works.

### [Official Amnezia docs](https://docs.amnezia.org/documentation/instructions/share-connection) | [Amnezia Client sources](https://github.com/amnezia-vpn/amnezia-client)

> [!TIP]
> The problem is documented in official issues: [amneziawg-android#56](https://github.com/amnezia-vpn/amneziawg-android/issues/56), [amnezia-client#2119](https://github.com/amnezia-vpn/amnezia-client/issues/2119). Amnezia writes: *"The QR code cannot be scanned if you selected AmneziaWG native format"*.

## Features

- Reads a `.vpn` file or a raw `vpn://...` string.
- Decodes base64url to zlib blob to JSON and extracts the hidden config.
- Verifies the result is `[Interface]` + `[Peer]`.
- Fixes unresolved placeholders `$PRIMARY_DNS` / `$SECONDARY_DNS` (`--dns`).
- Inserts/replaces `MTU` in `[Interface]` (`--mtu 1280`) — without it web traffic dies on mobile networks.
- Repairs a single corrupted base64url character on decode failure.
- Generates a QR PNG from the text config, not from `vpn://`.
- `--raw` flag — return the config unmodified.

## Quick start

```bash
pip install "qrcode[pil]"
python3 scripts/decode_amnezia_vpn.py export.vpn -o fixed.conf --png qr.png --mtu 1280
```

After that:

- `fixed.conf` — a working config for AmneziaWG / WireGuard.
- `qr.png` — a QR the AmneziaWG client imports.

## Links

- [https://docs.amnezia.org](https://docs.amnezia.org) — Amnezia documentation
- [https://github.com/amnezia-vpn/amneziawg-android/issues/56](https://github.com/amnezia-vpn/amneziawg-android/issues/56) — issue about the unimportable QR
- [https://github.com/donaldzou/WGDashboard/issues/753](https://github.com/donaldzou/WGDashboard/issues/753) — issue about "unknown section in config"

## Usage

```bash
# QR for a phone
python3 scripts/decode_amnezia_vpn.py export.vpn -o fixed.conf --png qr.png --mtu 1280

# Substitute your own DNS instead of $PRIMARY_DNS/$SECONDARY_DNS
python3 scripts/decode_amnezia_vpn.py export.vpn -o fixed.conf --dns "9.9.9.9, 149.112.112.112"

# Return as-is, without modifications
python3 scripts/decode_amnezia_vpn.py export.vpn --raw

# Repair a single corrupted base64url character
python3 scripts/decode_amnezia_vpn.py export.vpn -o fixed.conf
```

### Flags

| Flag | Purpose |
|------|---------|
| `source` | path to `.vpn` or a `vpn://...` string |
| `-o, --output-conf` | where to write `.conf` (stdout otherwise) |
| `--png` | write a QR PNG |
| `--dns "a, b"` | replace `$PRIMARY_DNS/$SECONDARY_DNS` (default `1.1.1.1, 8.8.8.8`) |
| `--mtu 1280` | insert/replace `MTU` in `[Interface]` |
| `--no-repair` | do not repair a corrupted base64url character |
| `--raw` | do not fix placeholders and MTU |

## Tech

QR Fix uses the Python standard library and one optional package:

- Python 3.10+
- [qrcode[pil]](https://pypi.org/project/qrcode/) — PNG generation

## How to import

- Preferred: copy `fixed.conf` into the AmneziaWG client (**Import from file**).
- Alternatively: scan `qr.png`.

## License

This project is licensed under the MIT License (see LICENSE).
