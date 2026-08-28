# AmneziaWG QR Fix

_Rеконструкция рабочего QR для AmneziaWG из сломанного экспорта_

### [Русский](README.md) | [English](README_EN.md)

Инструмент восстанавливает конфиг AmneziaWG из экспорта `vpn://...` / `.vpn` в обычный текстовый формат `[Interface]` + `[Peer]` и собирает из него QR, который клиент AmneziaWG реально импортирует.

> [!NOTE]
> Это **отдельная консольная программа на Python** (`scripts/decode_amnezia_vpn.py`). Для работы не нужен никакой ИИ. Файлы `SKILL.md` и `agents/openai.yaml` — опциональная обёртка для AI-агентов (Claude, Codex, OpenAI), чтобы ассистент мог вызвать скрипт за вас. Если вы не используете AI-агента — эти файлы можно игнорировать.

> [!TIP]
> Проблема описана в официальных issue: [amneziawg-android#56](https://github.com/amnezia-vpn/amneziawg-android/issues/56), [amnezia-client#2119](https://github.com/amnezia-vpn/amnezia-client/issues/2119). Сама Amnezia признаёт: _«The QR code cannot be scanned if you selected AmneziaWG native format»_.

## Installation

Требуется Python 3.10+. Для генерации PNG установите `qrcode[pil]`:

```
$ pip install "qrcode[pil]"
```

## Usage

Быстрый запуск — QR для телефона:

```
$ python3 scripts/decode_amnezia_vpn.py export.vpn -o fixed.conf --png qr.png --mtu 1280
```

После этого:

- `fixed.conf` — рабочая конфигурация для AmneziaWG / WireGuard;
- `qr.png` — QR, который клиент AmneziaWG импортирует.

## How it works

1. Читает `.vpn` файл или сырую строку `vpn://...`.
2. Снимает `vpn://`, декодирует base64url, разжимает zlib-блоб (с 4-байтным заголовком или без).
3. Находит скрытый конфиг и проверяет, что это `[Interface]` + `[Peer]`.
4. При неудачном декоде пробует восстановить один битый символ base64url.
5. Чинит нераскрытые плейсхолдеры `$PRIMARY_DNS` / `$SECONDARY_DNS` (по умолчанию `1.1.1.1, 8.8.8.8`, переопределение через `--dns`).
6. Вставляет/заменяет `MTU` в `[Interface]` (`--mtu 1280`) — без него на мобильных сетях рвётся веб-трафик.
7. Сохраняет `.conf` и, при необходимости, генерирует QR PNG из текста, а не из `vpn://`.

## Options

| Флаг | Назначение |
|------|-----------|
| `source` | путь к `.vpn` или строка `vpn://...` |
| `-o, --output-conf` | куда писать `.conf` (иначе stdout) |
| `--png` | записать QR PNG |
| `--dns "a, b"` | заменить `$PRIMARY_DNS/$SECONDARY_DNS` (дефолт `1.1.1.1, 8.8.8.8`) |
| `--mtu 1280` | вставить/заменить `MTU` в `[Interface]` |
| `--no-repair` | не чинить битый символ base64url |
| `--raw` | не чинить плейсхолдеры и MTU, вернуть как есть |

> [!TIP]
> Для импорта предпочтительнее скопировать `fixed.conf` в клиент AmneziaWG (**Import from file**). Скан `qr.png` — альтернатива.

> [!IMPORTANT]
> Конфиги с нераскрытыми `$UPPERCASE_VARS` отклоняются, если не чинить. QR собирается только из валидного текста с `[Interface]` и `[Peer]` — никогда из `vpn://` или JSON.

## Examples

```
# Подставить свои DNS
$ python3 scripts/decode_amnezia_vpn.py export.vpn -o fixed.conf --dns "9.9.9.9, 149.112.112.112"

# Вернуть конфиг без модификаций
$ python3 scripts/decode_amnezia_vpn.py export.vpn --raw
```

## License

Распространяется под лицензией MIT (см. [LICENSE](LICENSE)).
