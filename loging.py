import time
import requests
import dpath.util as dp
from random import randint
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import get_settings


def _make_session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "POST"]),
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    return s


def _extract_first(values: list, err: str) -> str:
    if not values:
        raise RuntimeError(err)
    return values[0]


def login(numbers: str) -> str:

    st = get_settings()

    if not str(numbers).isdigit():
        raise ValueError("Номер должен состоять только из цифр")

    if not st.bdpn_login or not st.bdpn_password:
        raise RuntimeError("Не заданы BDPN_LOGIN/BDPN_PASSWORD в .env")

    session = _make_session()
    req_id = randint(263953826, 663953826)

    headers = {
        "Accept": "application/json,text/plain,*/*",
        "Content-Type": "application/json",
        "Origin": "",
        "Referer": "",
        "User-Agent": st.user_agent,
    }
    payload = {
        "jsonrpc": "2.0",
        "id": int(req_id),
        "method": "login",
        "params": {"login": st.bdpn_login, "password": st.bdpn_password},
    }

    try:
        res = session.post(st.bdpn_url, json=payload, headers=headers, timeout=st.timeout_sec)
        res.raise_for_status()
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(
            f"Нет соединения с {st.bdpn_url} (сервер недоступен): {e}"
        ) from e
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"HTTP ошибка при login(): {e}") from e

    try:
        auth_list = dp.values(res.json(), "/result/**/auth")
    except Exception as e:
        raise RuntimeError(f"Не смог распарсить JSON login(): {res.text[:200]}") from e

    auth = _extract_first(auth_list, f"Сервер не вернул auth на login(): {res.text[:200]}")

    time.sleep(0.2)

    headers2 = {
        "Accept": "application/json,text/plain,*/*",
        "Content-Type": "application/json",
        "Origin": "",
        "Referer": "",
        "User-Agent": st.user_agent,
    }
    payload2 = {
        "jsonrpc": "2.0",
        "id": int(req_id),
        "method": "get_number_history",
        "params": {"auth": auth, "number": int(numbers)},
    }

    try:
        res2 = session.post(
            st.bdpn_url,
            json=payload2,
            headers=headers2,
            cookies={"UserCulture": "ru-RU", "auth": auth},
            timeout=st.timeout_sec,
        )
        res2.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"HTTP ошибка при get_number_history(): {e}") from e

    try:
        j = res2.json()
    except Exception as e:
        raise RuntimeError(f"Не смог распарсить JSON get_number_history(): {res2.text[:200]}") from e

    parse_region = dp.values(j, "/result/**/number_range_history")
    parse_numb = dp.values(j, "/result/**/number_history")
    if not parse_region or not parse_numb:
        raise RuntimeError(f"Пустой/неожиданный ответ истории по номеру: {j}")

    region = _extract_first(dp.values(parse_region[0][0], "/region/**/name"), "Нет region.name в ответе")
    date_from = _extract_first(dp.values(parse_numb[0][0], "/date_from"), "Нет date_from в ответе")
    oper = _extract_first(dp.values(parse_numb[0][0], "/org/**/name"), "Нет org.name в ответе")

    return f"{oper} {date_from} {region}"
