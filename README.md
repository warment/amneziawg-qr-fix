# AmneziaWG QR Fix

### _Восстановление рабочего QR для AmneziaWG_

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Version 1.2.0](https://img.shields.io/badge/version-1.2.0-green.svg)](https://github.com/warment/amneziawg-qr-fix/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

### [Русский](https://github.com/warment/amneziawg-qr-fix) | [Discussions](https://github.com/warment/amneziawg-qr-fix/discussions)

[AmneziaWG](https://docs.amnezia.org/documentation/amnezia-wg/) — обфусцированный протокол поверх WireGuard. Приложение AmneziaVPN экспортирует конфиг в QR-формате `vpn://...`, но клиент AmneziaWG такого QR не принимает — это известный баг, который Amnezia признаёт в собственной документации.

**QR Fix** распаковывает `vpn://...` обратно в обычный текстовый конфиг `[Interface]` + `[Peer]` и собирает из него QR, который реально импортируется.

### [Официальная документация Amnezia](https://docs.amnezia.org/documentation/instructions/share-connection) | [Исходники Amnezia Клиента](https://github.com/amnezia-vpn/amnezia-client)

> [!TIP]
> Проблема описана в официальных issue: [amneziawg-android#56](https://github.com/amnezia-vpn/amneziawg-android/issues/56), [amnezia-client#2119](https://github.com/amnezia-vpn/amnezia-client/issues/2119). Amnezia пишет: *«The QR code cannot be scanned if you selected AmneziaWG native format»*.

## Features

- Читает `.vpn` файл или сырую строку `vpn://...`.
- Декодирует base64url → zlib-блоб → JSON и вытаскивает скрытый конфиг.
- Проверяет, что результат это `[Interface]` + `[Peer]`.
- Чинит нераскрытые плейсхолдеры `$PRIMARY_DNS` / `$SECONDARY_DNS` (`--dns`).
- Вставляет/заменяет `MTU` в `[Interface]` (`--mtu 1280`) — без этого на мобильных рвётся веб-трафик.
- Восстанавливает один битый символ base64url при неудачном декоде.
- Генерирует QR PNG из текстового конфига, а не из `vpn://`.
- Флаг `--raw` — вернуть конфиг без модификаций.

## Quick start

```bash
pip install "qrcode[pil]"
python3 scripts/decode_amnezia_vpn.py export.vpn -o fixed.conf --png qr.png --mtu 1280
```

После этого:

- `fixed.conf` — рабочая конфигурация для AmneziaWG / WireGuard.
- `qr.png` — QR, который клиент AmneziaWG импортирует.

## Links

- [https://docs.amnezia.org](https://docs.amnezia.org) — документация Amnezia
- [https://github.com/amnezia-vpn/amneziawg-android/issues/56](https://github.com/amnezia-vpn/amneziawg-android/issues/56) — issue про неимпортируемый QR
- [https://github.com/donaldzou/WGDashboard/issues/753](https://github.com/donaldzou/WGDashboard/issues/753) — issue про «unknown section in config»

## Usage

```bash
# QR для телефона
python3 scripts/decode_amnezia_vpn.py export.vpn -o fixed.conf --png qr.png --mtu 1280

# Подставить свои DNS вместо $PRIMARY_DNS/$SECONDARY_DNS
python3 scripts/decode_amnezia_vpn.py export.vpn -o fixed.conf --dns "9.9.9.9, 149.112.112.112"

# Вернуть как есть, без модификаций
python3 scripts/decode_amnezia_vpn.py export.vpn --raw

# Восстановить один битый символ base64url
python3 scripts/decode_amnezia_vpn.py export.vpn -o fixed.conf
```

### Ключи

| Ключ | Назначение |
|------|-----------|
| `source` | путь к `.vpn` или строка `vpn://...` |
| `-o, --output-conf` | куда писать `.conf` (иначе stdout) |
| `--png` | записать QR PNG |
| `--dns "a, b"` | заменить `$PRIMARY_DNS/$SECONDARY_DNS` (дефолт `1.1.1.1, 8.8.8.8`) |
| `--mtu 1280` | вставить/заменить `MTU` в `[Interface]` |
| `--no-repair` | не чинить битый символ base64url |
| `--raw` | не чинить плейсхолдеры и MTU |

## Tech

QR Fix использует стандартную библиотеку Python и один опциональный пакет:

- Python 3.10+
- [qrcode[pil]](https://pypi.org/project/qrcode/) — генерация PNG

## Как импортировать

- Предпочтительно: скопировать `fixed.conf` в клиент AmneziaWG (**Import from file**).
- Альтернативно: отсканировать `qr.png`.

## License

This project is licensed under the MIT License (see LICENSE).
