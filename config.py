import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv(dotenv_path: str = ".env") -> None:
    """
    Мини-лоадер .env без внешних зависимостей.
    Поддерживает строки вида KEY=VALUE и KEY="VALUE".
    """
    p = Path(dotenv_path)
    if not p.exists():
        return

    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        os.environ.setdefault(k, v)


_load_dotenv()


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str

    bdpn_url: str
    bdpn_login: str
    bdpn_password: str

    timeout_sec: float
    user_agent: str

    # id админов (через запятую)
    admin_ids: set[int]
    blacklist_ids: set[int]


def _parse_int_set(value: str) -> set[int]:
    out: set[int] = set()
    for part in (value or "").split(","):
        part = part.strip()
        if part:
            out.add(int(part))
    return out


def get_settings() -> Settings:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Не задан TELEGRAM_BOT_TOKEN (см. .env.example)")

    return Settings(
        telegram_bot_token=token,
        bdpn_url=os.getenv("BDPN_URL", "https://prod.bdpn.ru/bdpn_wb").strip(),
        bdpn_login=os.getenv("BDPN_LOGIN", "").strip(),
        bdpn_password=os.getenv("BDPN_PASSWORD", "").strip(),
        timeout_sec=float(os.getenv("BDPN_TIMEOUT", "20")),
        user_agent=os.getenv(
            "BDPN_UA",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ).strip(),
        admin_ids=_parse_int_set(os.getenv("ADMIN_IDS", "")),
        blacklist_ids=_parse_int_set(os.getenv("BLACKLIST_IDS", "")),
    )
