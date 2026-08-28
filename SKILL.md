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
7. Fix unresolved placeholders: Amnezia client often exports literal `$PRIMARY_DNS, $SECONDARY_DNS` in the `DNS` line — replace them (default `1.1.1.1, 8.8.8.8`, override via `--dns`). Such a config is dead until fixed.
8. Patch MTU (`--mtu 1280`) for mobile clients: without it handshakes pass but web traffic silently dies on carrier networks.
9. Save it as `.conf`.
10. Generate QR only from the `.conf` text.

## If Decode Fails

- Try a one-character repair of the base64url body before giving up.
- Accept a repair only if it yields JSON with a usable `config` value.

## Validation Rules

- Reject `vpn://...` as a QR payload.
- Reject JSON as a QR payload.
- Reject base64 as a QR payload.
- Accept only plain text with `[Interface]` and `[Peer]`.
- Reject configs containing unresolved `$UPPERCASE_VARS` unless they are being fixed.
- For phone clients prefer adding `MTU = 1280` before generating the QR.
- Prefer importing `.conf` directly when it is available.

## Script

Use `scripts/decode_amnezia_vpn.py` to:

- decode a `.vpn` file or raw `vpn://...` input,
- extract the hidden config,
- validate the result,
- fix unresolved `$PRIMARY_DNS` / `$SECONDARY_DNS` placeholders (on by default; `--dns "1.1.1.1, 8.8.8.8"` to override),
- insert or replace `MTU` in `[Interface]` (`--mtu 1280`),
- optionally repair one wrong base64url character,
- skip all fixes with `--raw`,
- optionally write a QR PNG when `qrcode` is available.

Typical usage for a phone that "connects but has no internet":

```bash
python3 scripts/decode_amnezia_vpn.py export.vpn -o fixed.conf --png qr.png --mtu 1280
```

## Resources

### scripts/

Executable code for Amnezia export recovery and validation.
