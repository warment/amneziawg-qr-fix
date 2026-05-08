---
name: amneziawg-qr-fix
description: Decode Amnezia `vpn://...` or `.vpn` exports into a valid `.conf` and QR-ready plain-text config. Use when an AmneziaWG QR import fails, when a QR contains `vpn://...`, base64, or JSON instead of a WireGuard-style config, or when recovering the hidden `config` field from an Amnezia export.
---

# AmneziaWG QR Fix

## Goal

Recover the real Amnezia config fast, then build the QR from the plain `.conf` text.

## Fast Path

1. Read the source from a `.vpn` file or a raw `vpn://...` string.
2. Strip `vpn://`.
3. Base64url-decode the payload.
4. Decompress the JSON blob with `zlib` after the 4-byte header. If that fails, try the raw stream too.
5. Find the inner config string.
6. Confirm the result contains `[Interface]` and `[Peer]`.
7. Save it as `.conf`.
8. Generate QR only from the `.conf` text.

## If Decode Fails

- Try a one-character repair of the base64url body before giving up.
- Accept a repair only if it yields JSON with a usable `config` value.

## Validation Rules

- Reject `vpn://...` as a QR payload.
- Reject JSON as a QR payload.
- Reject base64 as a QR payload.
- Accept only plain text with `[Interface]` and `[Peer]`.
- Prefer importing `.conf` directly when it is available.

## Script

Use `scripts/decode_amnezia_vpn.py` to:

- decode a `.vpn` file or raw `vpn://...` input,
- extract the hidden config,
- validate the result,
- optionally repair one wrong base64url character,
- optionally write a QR PNG when `qrcode` is available.

## Resources

### scripts/

Executable code for Amnezia export recovery and validation.
