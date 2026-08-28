#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import re
import sys
import zlib
from pathlib import Path


BASE64URL_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"

# Значения по умолчанию для нераскрытых переменных Amnezia-клиента
DEFAULT_DNS = ["1.1.1.1", "8.8.8.8"]


def read_source(value: str) -> str:
    path = Path(value)
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return value.strip()


def normalize_input(text: str) -> str:
    text = text.strip()
    if text.startswith("vpn://"):
        text = text.removeprefix("vpn://")
    return text.replace("\n", "").replace("\r", "")


def b64url_decode(body: str) -> bytes:
    padded = body + "=" * ((4 - len(body) % 4) % 4)
    return base64.urlsafe_b64decode(padded)


def decode_json_blob(raw: bytes) -> str:
    candidates = []
    if len(raw) > 4:
        candidates.append(raw[4:])
    candidates.append(raw)

    for candidate in candidates:
        try:
            return zlib.decompress(candidate).decode("utf-8")
        except Exception:
            pass

    raise ValueError("could not decompress Amnezia payload")


def looks_like_config(text: str) -> bool:
    candidate = text.lstrip("\ufeff \t\r\n")
    return candidate.startswith("[Interface]") and "[Peer]" in candidate


def find_config(node):
    if isinstance(node, str):
        stripped = node.strip()
        if looks_like_config(stripped):
            return stripped
        try:
            parsed = json.loads(stripped)
        except Exception:
            return None
        return find_config(parsed)

    if isinstance(node, list):
        for item in node:
            found = find_config(item)
            if found:
                return found
        return None

    if isinstance(node, dict):
        for key in ("config", "last_config"):
            if key in node:
                found = find_config(node[key])
                if found:
                    return found
        for value in node.values():
            found = find_config(value)
            if found:
                return found
        return None

    return None


def decode_payload(encoded: str):
    raw = b64url_decode(encoded)
    json_text = decode_json_blob(raw)
    data = json.loads(json_text)
    config = find_config(data)
    if not config:
        raise ValueError("config field not found")
    if not looks_like_config(config):
        raise ValueError("decoded config does not look like an AmneziaWG config")
    return data, config


def try_single_char_repair(encoded: str):
    for index, original in enumerate(encoded):
        if original not in BASE64URL_ALPHABET:
            continue
        for replacement in BASE64URL_ALPHABET:
            if replacement == original:
                continue
            candidate = encoded[:index] + replacement + encoded[index + 1 :]
            try:
                data, config = decode_payload(candidate)
                return candidate, index, original, replacement, data, config
            except Exception:
                continue
    return None


def maybe_write_qr_png(config_text: str, png_path: str):
    try:
        import qrcode
        from qrcode.constants import ERROR_CORRECT_M
    except Exception as exc:
        raise RuntimeError(
            "qrcode module is not available; install qrcode[pil] or skip --png"
        ) from exc

    img = qrcode.make(config_text, error_correction=ERROR_CORRECT_M)
    img.save(png_path)


def fix_placeholders(config_text: str, dns_values: list[str]) -> tuple[str, list[str]]:
    """Заменяет нераскрытые переменные вида $PRIMARY_DNS на реальные значения.

    Amnezia-клиент при экспорте иногда оставляет литералы $PRIMARY_DNS /
    $SECONDARY_DNS вместо адресов — такой конфиг не работает.
    Возвращает (новый_текст, список_заменённых_переменных).
    """
    found = sorted(set(re.findall(r"\$[A-Z_][A-Z0-9_]*", config_text)))
    if not found:
        return config_text, []

    fixed = config_text
    # DNS-переменные подставляем из --dns (или дефолтов)
    mapping = {}
    if "$PRIMARY_DNS" in found and dns_values:
        mapping["$PRIMARY_DNS"] = dns_values[0]
    if "$SECONDARY_DNS" in found:
        mapping["$SECONDARY_DNS"] = dns_values[1] if len(dns_values) > 1 else dns_values[0]

    for var, value in mapping.items():
        fixed = fixed.replace(var, value)

    remaining = sorted(set(re.findall(r"\$[A-Z_][A-Z0-9_]*", fixed)))
    return fixed, remaining


def apply_mtu(config_text: str, mtu: int) -> tuple[str, str]:
    """Вставляет или заменяет строку MTU в секции [Interface].

    Возвращает (новый_текст, что_сделано): "inserted" | "replaced" | "unchanged".
    Без MTU мобильные сети часто рвут крупные пакеты: handshake проходит,
    а веб-трафик умирает. Безопасное значение — 1280.
    """
    mtu_line = f"MTU = {mtu}"
    lines = config_text.splitlines()
    out: list[str] = []
    action = "inserted"
    inserted = False
    in_interface = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("["):
            in_interface = stripped == "[Interface]"
        if stripped.upper().startswith("MTU"):
            if not inserted:
                out.append(mtu_line)
                inserted = True
                action = "replaced"
            continue  # лишние MTU-строки выбрасываем
        if (
            not inserted
            and in_interface
            and stripped.lower().startswith("address")
        ):
            out.append(line)
            out.append(mtu_line)
            inserted = True
            continue
        out.append(line)

    if not inserted:
        # [Interface] не нашёлся — добавляем в самое начало
        out.insert(0, mtu_line)
    return "\n".join(out) + "\n", action


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Decode Amnezia vpn:// exports into plain config and optional QR."
    )
    parser.add_argument("source", help="Path to a .vpn file or a raw vpn:// string")
    parser.add_argument("-o", "--output-conf", help="Write the recovered .conf here")
    parser.add_argument("--png", help="Write a QR PNG for the recovered config")
    parser.add_argument(
        "--no-repair",
        action="store_true",
        help="Do not try one-character base64url repair if direct decode fails",
    )
    parser.add_argument(
        "--dns",
        default=", ".join(DEFAULT_DNS),
        help="DNS через запятую для подстановки вместо $PRIMARY_DNS/$SECONDARY_DNS",
    )
    parser.add_argument(
        "--mtu",
        type=int,
        default=None,
        help="Вставить/заменить MTU (рекомендуется 1280 для мобильных сетей)",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Не чинить плейсхолдеры и не трогать MTU — вернуть как есть",
    )
    args = parser.parse_args()

    source_text = read_source(args.source)
    encoded = normalize_input(source_text)

    try:
        data, config = decode_payload(encoded)
        repaired = None
    except Exception as first_error:
        if args.no_repair:
            raise
        repaired = try_single_char_repair(encoded)
        if not repaired:
            raise first_error
        encoded, index, original, replacement, data, config = repaired
        print(
            f"repaired base64url character at position {index}: {original!r} -> {replacement!r}",
            file=sys.stderr,
        )

    # Постобработка: чиним плейсхолдеры и MTU (если не попросили --raw)
    if not args.raw:
        dns_values = [d.strip() for d in args.dns.split(",") if d.strip()]
        config, remaining = fix_placeholders(config, dns_values)
        if remaining:
            print(
                f"ВНИМАНИЕ: остались нераскрытые переменные: {', '.join(remaining)}",
                file=sys.stderr,
            )
        if args.mtu:
            config, mtu_action = apply_mtu(config, args.mtu)
            print(f"MTU {args.mtu}: {mtu_action}", file=sys.stderr)

    if args.output_conf:
        Path(args.output_conf).write_text(config + "\n", encoding="utf-8")
    else:
        sys.stdout.write(config)
        if not config.endswith("\n"):
            sys.stdout.write("\n")

    if args.png:
        maybe_write_qr_png(config, args.png)

    # Keep the parsed JSON reachable for debugging in future edits.
    _ = data
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
