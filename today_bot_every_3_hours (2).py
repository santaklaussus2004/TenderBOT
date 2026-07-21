from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from telegram import Bot, LinkPreviewOptions, Update
from telegram.ext import Application, CommandHandler, ContextTypes, filters
from telegram.error import RetryAfter, TelegramError

MAX_MESSAGE_LENGTH = 3900
NO_LINK_PREVIEW = LinkPreviewOptions(is_disabled=True)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def value_or_default(value: Any, default: str = "Не указано") -> str:
    if value is None:
        return default

    if isinstance(value, str):
        value = value.strip()
        return value if value else default

    return str(value)


def boolean_text(
    value: Any,
    true_text: str = "Да",
    false_text: str = "Нет",
    unknown_text: str = "Неизвестно",
) -> str:
    if value is True:
        return true_text
    if value is False:
        return false_text
    return unknown_text


def split_text(text: str, limit: int = MAX_MESSAGE_LENGTH) -> Iterator[str]:
    remaining = text.strip()

    while len(remaining) > limit:
        cut_position = remaining.rfind("\n", 0, limit)

        if cut_position < limit // 2:
            cut_position = limit

        part = remaining[:cut_position].strip()
        if part:
            yield part

        remaining = remaining[cut_position:].strip()

    if remaining:
        yield remaining

def get_trash_json_path() -> Path:
    return get_data_directory() / "trash.json"


def get_retry_seconds(error: RetryAfter) -> float:
    retry_after = error.retry_after

    if hasattr(retry_after, "total_seconds"):
        return retry_after.total_seconds()

    return float(retry_after)


async def send_long_message(update: Update, text: str) -> None:
    message = update.effective_message

    if message is None:
        return

    for part in split_text(text):
        while True:
            try:
                await message.reply_text(
                    part,
                    link_preview_options=NO_LINK_PREVIEW,
                )
                break

            except RetryAfter as error:
                delay = get_retry_seconds(error) + 1

                logger.warning(
                    "Telegram требует паузу %.1f секунд",
                    delay,
                )

                await asyncio.sleep(delay)

        await asyncio.sleep(1.1)


async def send_long_chat_message(
    bot: Bot,
    chat_id: int,
    text: str,
) -> None:
    for part in split_text(text):
        while True:
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=part,
                    link_preview_options=NO_LINK_PREVIEW,
                )
                break

            except RetryAfter as error:
                delay = get_retry_seconds(error) + 1

                logger.warning(
                    "Telegram требует паузу %.1f секунд для чата %s",
                    delay,
                    chat_id,
                )

                await asyncio.sleep(delay)

        await asyncio.sleep(1.1)

def get_allowed_user_ids() -> set[int]:
    raw_ids = os.getenv("ALLOWED_TELEGRAM_IDS", "").strip()

    allowed_ids: set[int] = set()

    for raw_id in raw_ids.split(","):
        raw_id = raw_id.strip()

        if not raw_id:
            continue

        try:
            allowed_ids.add(int(raw_id))
        except ValueError:
            logger.warning(
                "Некорректный Telegram ID в ALLOWED_TELEGRAM_IDS: %s",
                raw_id,
            )

    return allowed_ids


def get_bot_timezone() -> ZoneInfo:
    timezone_name = os.getenv("BOT_TIMEZONE", "Asia/Qyzylorda").strip()

    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        logger.exception(
            "Часовой пояс %s не найден. Используется UTC.",
            timezone_name,
        )
        return ZoneInfo("UTC")


def get_data_directory() -> Path:
    return Path(os.getenv("DATA_DIR", ".")).expanduser()


def get_state_directory() -> Path:
    state_directory = Path(
        os.getenv("BOT_STATE_DIR", str(get_data_directory()))
    ).expanduser()
    state_directory.mkdir(parents=True, exist_ok=True)
    return state_directory


def get_today_json_path() -> tuple[Path, str]:
    timezone = get_bot_timezone()
    date_text = datetime.now(timezone).strftime("%d.%m.%Y")

    # Для автоматической ежедневной смены файла TODAY_FILE лучше не задавать.
    explicit_file = os.getenv("TODAY_FILE", "").strip()
    if explicit_file:
        return Path(explicit_file).expanduser(), date_text

    return get_data_directory() / f"{date_text}.json", date_text



def get_past_json_path() -> Path:
    """
    Файл с тендерами за последние полгода.
    По умолчанию: 17.01.2026past.json
    """

    today = datetime.now()
    filename = Path((today - relativedelta(months=6)).strftime("%d.%m.%Y") +"past.json")
   
    path = Path(filename).expanduser()

    if not path.is_absolute():
        path = get_data_directory() / path

    return path


def get_before_json_files() -> list[tuple[datetime, Path]]:
    """
    Находит все дневные JSON-файлы до сегодняшней даты.

    Подходящие названия:
    16.07.2026.json
    15.07.2026.json

    Не подходят:
    17.01.2026past.json
    telegram_subscribers.json
    telegram_check_state.json
    сегодняшний файл
    """

    timezone = get_bot_timezone()
    today = datetime.now(timezone).date()

    found_files: list[tuple[datetime, Path]] = []

    for path in get_data_directory().glob("*.json"):
        try:
            file_date = datetime.strptime(
                path.stem,
                "%d.%m.%Y",
            )
        except ValueError:
            # Пропускаем файлы, название которых не является датой.
            continue

        if file_date.date() >= today:
            # Сегодняшний и будущие файлы не добавляем.
            continue

        found_files.append((file_date, path))

    # Сначала самые новые файлы.
    found_files.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return found_files

















def get_subscribers_path() -> Path:
    return get_state_directory() / "telegram_subscribers.json"


def get_check_state_path() -> Path:
    return get_state_directory() / "telegram_check_state.json"


def read_json_file(path: Path, default: Any) -> Any:
    if not path.exists():
        return default

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        logger.exception("Не удалось прочитать JSON-файл %s", path)
        return default


def write_json_file(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")

    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    temporary_path.replace(path)


def load_tenders(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("В корне JSON должен находиться список тендеров.")

    return [item for item in data if isinstance(item, dict)]


def load_subscribers() -> set[int]:
    raw_subscribers = read_json_file(get_subscribers_path(), [])

    if not isinstance(raw_subscribers, list):
        return set()

    subscribers: set[int] = set()

    for value in raw_subscribers:
        try:
            subscribers.add(int(value))
        except (TypeError, ValueError):
            continue

    return subscribers


def save_subscribers(subscribers: set[int]) -> None:
    write_json_file(get_subscribers_path(), sorted(subscribers))


def subscribe_chat(chat_id: int) -> bool:
    subscribers = load_subscribers()
    was_added = chat_id not in subscribers
    subscribers.add(chat_id)
    save_subscribers(subscribers)
    return was_added


def unsubscribe_chat(chat_id: int) -> bool:
    subscribers = load_subscribers()

    if chat_id not in subscribers:
        return False

    subscribers.remove(chat_id)
    save_subscribers(subscribers)
    return True


def tender_key(tender: dict[str, Any]) -> str:
    url = tender.get("url")
    if isinstance(url, str) and url.strip():
        return f"url:{url.strip()}"

    general = tender.get("general")
    if isinstance(general, dict):
        announcement_number = general.get("номер объявления")
        if isinstance(announcement_number, str) and announcement_number.strip():
            return f"number:{announcement_number.strip()}"

    stable_text = json.dumps(
        tender,
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )
    digest = hashlib.sha256(stable_text.encode("utf-8")).hexdigest()
    return f"hash:{digest}"


def load_check_state() -> dict[str, Any]:
    state = read_json_file(
        get_check_state_path(),
        {
            "date": None,
            "known_tender_keys": [],
        },
    )

    if not isinstance(state, dict):
        return {
            "date": None,
            "known_tender_keys": [],
        }

    return state


def save_check_state(date_text: str, tenders: list[dict[str, Any]]) -> None:
    keys = [tender_key(tender) for tender in tenders]

    write_json_file(
        get_check_state_path(),
        {
            "date": date_text,
            "known_tender_keys": list(dict.fromkeys(keys)),
            "checked_at": datetime.now(get_bot_timezone()).isoformat(),
        },
    )


def format_tender_header(
    tender: dict[str, Any],
    index: int,
    total: int,
) -> str:
    general = tender.get("general")
    if not isinstance(general, dict):
        general = {}

    return "\n".join(
        [
            f"📢 ТЕНДЕР {index} ИЗ {total}",
            "",
            f"Номер объявления: {value_or_default(general.get('номер объявления'))}",
            f"Наименование: {value_or_default(general.get('наименование объявления'))}",
            f"Статус объявления: {value_or_default(general.get('статус объявления'))}",
            f"Дата публикации: {value_or_default(general.get('дата публикации объявления'))}",
            f"Начало приёма заявок: {value_or_default(general.get('срок начала приема заявок'))}",
            f"Окончание приёма заявок: {value_or_default(general.get('срок окончания приема заявок'))}",
            f"Ссылка на объявление: {value_or_default(tender.get('url'))}",
        ]
    )


def format_document(
    document: dict[str, Any],
    index: int,
    total: int,
) -> str:
    return "\n".join(
        [
            f"📄 ДОКУМЕНТ {index} ИЗ {total}",
            "",
            f"Название файла: {value_or_default(document.get('name'))}",
            f"Ссылка на файл: {value_or_default(document.get('url'))}",
            "",
            "Краткое описание:",
            value_or_default(document.get("summary"), "Описание отсутствует"),
        ]
    )


def get_winner_websites(winner: dict[str, Any]) -> list[str]:
    websites: list[str] = []

    direct_link = winner.get("web_link")
    if isinstance(direct_link, str) and direct_link.strip():
        websites.append(direct_link.strip())

    extra_links = winner.get("winner_websites")
    if isinstance(extra_links, list):
        for link in extra_links:
            if isinstance(link, str) and link.strip():
                websites.append(link.strip())

    return list(dict.fromkeys(websites))


def format_winner(
    winner: dict[str, Any],
    index: int,
    total: int,
) -> str:
    violations = winner.get("violations")

    if isinstance(violations, list) and violations:
        violations_text = "\n".join(
            f"• {value_or_default(item)}" for item in violations
        )
    else:
        violations_text = "Не указаны"

    websites = get_winner_websites(winner)
    websites_text = "\n".join(websites) if websites else "Не указан"

    lines = [
        f"🏆 ПОБЕДИТЕЛЬ {index} ИЗ {total}",
        "",
        f"Номер лота: {value_or_default(winner.get('lot_number'))}",
        f"Наименование лота: {value_or_default(winner.get('lot_name'))}",
        f"Сумма: {value_or_default(winner.get('amount'))} ₸",
        f"Статус лота: {value_or_default(winner.get('status'))}",
        f"Победитель: {value_or_default(winner.get('winner_name'))}",
        f"Второе место: {value_or_default(winner.get('second_place_name'))}",
        f"БИН/ИИН победителя: {value_or_default(winner.get('winner_iin'))}",
        f"Телефон: {value_or_default(winner.get('phone_number'))}",
        f"Электронная почта: {value_or_default(winner.get('email'))}",
        f"Компания активна: {boolean_text(winner.get('is_active'))}",
        (
            "Есть нарушения: "
            + boolean_text(
                winner.get("has_violations"),
                true_text="Да",
                false_text="Нет",
            )
        ),
        f"Дата окончания регистрации: {value_or_default(winner.get('registration_end_date'))}",
        "",
        "Нарушения:",
        violations_text,
        "",
        "Сайт компании:",
        websites_text,
    ]

    advertisement = winner.get("message")
    if isinstance(advertisement, str) and advertisement.strip():
        lines.extend(
            [
                "",
                "Подготовленное сообщение для победителя:",
                advertisement.strip(),
            ]
        )

    return "\n".join(lines)


async def send_tenders_to_chat(
    bot: Bot,
    chat_id: int,
    tenders: list[dict[str, Any]],
    date_text: str,
    heading: str,
) -> None:
    await send_long_chat_message(
        bot,
        chat_id,
        f"{heading}\n"
        f"📅 Дата: {date_text}\n"
        f"Найдено объявлений: {len(tenders)}",
    )

    for tender_index, tender in enumerate(tenders, start=1):
        await send_long_chat_message(
            bot,
            chat_id,
            format_tender_header(
                tender,
                tender_index,
                len(tenders),
            ),
        )

        documents = tender.get("documents")

        if isinstance(documents, list) and documents:
            await send_long_chat_message(
                bot,
                chat_id,
                f"📚 Документы объявления: {len(documents)}",
            )

            for document_index, document in enumerate(documents, start=1):
                if not isinstance(document, dict):
                    continue

                await send_long_chat_message(
                    bot,
                    chat_id,
                    format_document(
                        document,
                        document_index,
                        len(documents),
                    ),
                )
        else:
            await send_long_chat_message(
                bot,
                chat_id,
                "📚 Документы отсутствуют.",
            )

        winners = tender.get("winners")

        if isinstance(winners, list) and winners:
            await send_long_chat_message(
                bot,
                chat_id,
                f"🏅 Победители и лоты: {len(winners)}",
            )

            for winner_index, winner in enumerate(winners, start=1):
                if not isinstance(winner, dict):
                    continue

                await send_long_chat_message(
                    bot,
                    chat_id,
                    format_winner(
                        winner,
                        winner_index,
                        len(winners),
                    ),
                )
        else:
            await send_long_chat_message(
                bot,
                chat_id,
                "🏅 Победители отсутствуют.",
            )


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    del context

    chat = update.effective_chat
    if chat is None:
        return

    was_added = subscribe_chat(chat.id)

    if was_added:
        subscription_text = (
            "Вы подписаны на автоматические уведомления о новых тендерах."
        )
    else:
        subscription_text = (
            "Автоматические уведомления уже были включены."
        )

    await send_long_message(
        update,
        "Здравствуйте!\n\n"
        "/today — тендеры из сегодняшнего JSON-файла.\n"
        "/before — тендеры из всех прошлых дневных JSON-файлов.\n"
        "/past — тендеры за последние полгода.\n"
        "/stop — отключить автоматические уведомления.\n\n"
        "/trash — тендеры, которые не прошли проверку LLM.\n"
        f"{subscription_text}\n"
        "Бот проверяет сегодняшний JSON-файл каждые 3 часа.",
)


async def stop_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    del context

    chat = update.effective_chat
    if chat is None:
        return

    was_removed = unsubscribe_chat(chat.id)

    if was_removed:
        text = "Автоматические уведомления отключены."
    else:
        text = "Автоматические уведомления уже были отключены."

    await send_long_message(update, text)


async def today_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    chat = update.effective_chat
    if chat is None:
        return

    subscribe_chat(chat.id)

    json_path, date_text = get_today_json_path()

    if not json_path.exists():
        await send_long_message(
            update,
            "Файл с тендерами за сегодня не найден.\n\n"
            f"Ожидаемый файл: {json_path.resolve()}\n"
            f"Дата: {date_text}",
        )
        return

    try:
        tenders = load_tenders(json_path)
    except json.JSONDecodeError as error:
        logger.exception("Некорректный JSON: %s", json_path)
        await send_long_message(
            update,
            f"Не удалось прочитать JSON: ошибка в строке "
            f"{error.lineno}, столбце {error.colno}.",
        )
        return
    except (OSError, ValueError) as error:
        logger.exception("Не удалось открыть файл %s", json_path)
        await send_long_message(
            update,
            f"Не удалось открыть файл с тендерами: {error}",
        )
        return

    if not tenders:
        await send_long_message(
            update,
            f"За {date_text} тендеры не найдены.",
        )
        save_check_state(date_text, tenders)
        return

    await send_tenders_to_chat(
        context.bot,
        chat.id,
        tenders,
        date_text,
        heading="📅 Тендеры за сегодня",
    )

    # После /today текущие записи считаются уже просмотренными.
    save_check_state(date_text, tenders)

    await send_long_message(
        update,
        "✅ Все тендеры за сегодня отправлены.\n"
        "Автоматическая проверка новых записей выполняется каждые 3 часа.",
    )




async def past_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    chat = update.effective_chat
    if chat is None:
        return

    json_path = get_past_json_path()

    if not json_path.exists():
        await send_long_message(
            update,
            "Файл с тендерами за последние полгода не найден.\n\n"
            f"Ожидаемый файл: {json_path.resolve()}",
        )
        return

    try:
        tenders = load_tenders(json_path)

    except json.JSONDecodeError as error:
        logger.exception(
            "Некорректный JSON: %s",
            json_path,
        )

        await send_long_message(
            update,
            f"Ошибка JSON в строке {error.lineno}, "
            f"столбце {error.colno}.",
        )
        return

    except (OSError, ValueError) as error:
        logger.exception(
            "Не удалось открыть файл %s",
            json_path,
        )

        await send_long_message(
            update,
            f"Не удалось открыть файл: {error}",
        )
        return

    if not tenders:
        await send_long_message(
            update,
            "В файле за последние полгода тендеры не найдены.",
        )
        return

    date_text = json_path.stem.removesuffix("past")

    await send_tenders_to_chat(
        context.bot,
        chat.id,
        tenders,
        date_text,
        heading="📆 Тендеры за последние полгода",
    )

    await send_long_message(
        update,
        "✅ Все тендеры из файла за последние полгода отправлены.",
    )





async def before_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    chat = update.effective_chat
    if chat is None:
        return

    json_files = get_before_json_files()

    if not json_files:
        await send_long_message(
            update,
            "Прошлые дневные файлы с тендерами не найдены.",
        )
        return

    await send_long_message(
        update,
        "📁 Найдены прошлые дневные файлы: "
        f"{len(json_files)}.\n"
        "Начинаю отправку с самого нового.",
    )

    sent_files = 0
    sent_tenders = 0

    for file_date, json_path in json_files:
        try:
            tenders = load_tenders(json_path)

        except (
            OSError,
            ValueError,
            json.JSONDecodeError,
        ):
            logger.exception(
                "Не удалось прочитать архивный файл %s",
                json_path,
            )

            await send_long_message(
                update,
                f"⚠️ Не удалось прочитать файл: {json_path.name}",
            )
            continue

        if not tenders:
            continue

        date_text = file_date.strftime("%d.%m.%Y")

        await send_tenders_to_chat(
            context.bot,
            chat.id,
            tenders,
            date_text,
            heading="📂 Тендеры за прошлый день",
        )

        sent_files += 1
        sent_tenders += len(tenders)

    if sent_files == 0:
        await send_long_message(
            update,
            "Прошлые файлы найдены, но в них нет тендеров.",
        )
        return

    await send_long_message(
        update,
        "✅ Архивные тендеры отправлены.\n"
        f"Обработано файлов: {sent_files}\n"
        f"Отправлено тендеров: {sent_tenders}",
    )












async def check_today_file_job(
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    json_path, date_text = get_today_json_path()

    if not json_path.exists():
        logger.info(
            "Файл за сегодня пока не найден: %s",
            json_path,
        )
        return

    try:
        tenders = load_tenders(json_path)
    except (OSError, ValueError, json.JSONDecodeError):
        logger.exception(
            "Не удалось проверить файл %s",
            json_path,
        )
        return

    current_keys = [tender_key(tender) for tender in tenders]
    current_key_set = set(current_keys)

    state = load_check_state()
    state_date = state.get("date")
    known_keys_raw = state.get("known_tender_keys", [])

    known_keys = (
        set(known_keys_raw)
        if isinstance(known_keys_raw, list)
        else set()
    )

    # При наступлении нового дня создаём начальную точку.
    # Старые записи нового файла автоматически не рассылаются:
    # пользователь может получить их командой /today.
    if state_date != date_text:
        save_check_state(date_text, tenders)
        logger.info(
            "Новый день %s. Зафиксировано тендеров: %s",
            date_text,
            len(tenders),
        )
        return

    new_tenders = [
        tender
        for tender in tenders
        if tender_key(tender) not in known_keys
    ]

    # Состояние обновляется даже при удалении/изменении записей в файле.
    save_check_state(date_text, tenders)

    if not new_tenders:
        logger.info(
            "Новых тендеров за %s нет. Всего в файле: %s",
            date_text,
            len(current_key_set),
        )
        return

    subscribers = load_subscribers()

    if not subscribers:
        logger.info(
            "Найдено новых тендеров: %s, но подписчиков нет.",
            len(new_tenders),
        )
        return

    logger.info(
        "Найдено новых тендеров: %s. Подписчиков: %s",
        len(new_tenders),
        len(subscribers),
    )

    unavailable_chats: set[int] = set()

    for chat_id in subscribers:
        try:
            await send_tenders_to_chat(
                context.bot,
                chat_id,
                new_tenders,
                date_text,
                heading="🆕 В сегодняшнем файле появились новые тендеры",
            )
        except TelegramError:
            logger.exception(
                "Не удалось отправить уведомление в чат %s",
                chat_id,
            )
            unavailable_chats.add(chat_id)

    if unavailable_chats:
        subscribers.difference_update(unavailable_chats)
        save_subscribers(subscribers)


async def id_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    user = update.effective_user

    if user is None:
        return

    await update.effective_message.reply_text(
        f"Твой Telegram ID: {user.id}"
    )

async def trash_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    del context

    json_path = get_trash_json_path()

    if not json_path.exists():
        await send_long_message(
            update,
            "Файл trash.json не найден.\n\n"
            f"Ожидаемый путь: {json_path.resolve()}",
        )
        return

    try:
        trash_text = json_path.read_text(
            encoding="utf-8"
        ).strip()

    except OSError as error:
        logger.exception(
            "Не удалось прочитать файл %s",
            json_path,
        )

        await send_long_message(
            update,
            f"Не удалось открыть trash.json: {error}",
        )
        return

    if not trash_text:
        await send_long_message(
            update,
            "Файл trash.json существует, но он пуст.",
        )
        return

    await send_long_message(
        update,
        "🗑 В файле trash.json хранятся тендеры, которые "
        "не прошли проверку LLM и были признаны не относящимися "
        "к направлениям нашей компании.\n\n"
        f"Содержимое файла: {json_path.resolve()}",
    )

    # Отправляем всё содержимое trash.json как есть.
    await send_long_message(
        update,
        trash_text,
    )

    await send_long_message(
        update,
        "✅ Всё содержимое trash.json отправлено.",
    )


async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    logger.error(
        "Ошибка при обработке обновления %s",
        update,
        exc_info=context.error,
    )


def main() -> None:
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

    if not token:
        raise RuntimeError(
            "Переменная TELEGRAM_BOT_TOKEN не задана. "
            "Создайте файл .env и добавьте в него новый токен."
        )

    try:
        check_interval_seconds = int(
            os.getenv("CHECK_INTERVAL_SECONDS", "10800")
        )
    except ValueError as error:
        raise RuntimeError(
            "CHECK_INTERVAL_SECONDS должен быть целым числом."
        ) from error

    if check_interval_seconds < 60:
        raise RuntimeError(
            "CHECK_INTERVAL_SECONDS не должен быть меньше 60 секунд."
        )

    application = Application.builder().token(token).build()

    allowed_user_ids = get_allowed_user_ids()

    if not allowed_user_ids:
        raise RuntimeError(
            "В .env не указаны разрешённые Telegram ID: "
            "ALLOWED_TELEGRAM_IDS=123456789"
        )

    allowed_users_filter = (
        filters.User(user_id=allowed_user_ids)
        & filters.ChatType.PRIVATE
    )
    application.add_handler(
    CommandHandler("id", id_command)
)

    application.add_handler(
        CommandHandler(
            "start",
            start_command,
            filters=allowed_users_filter,
        )
    )

    application.add_handler(
        CommandHandler(
            "today",
            today_command,
            filters=allowed_users_filter,
        )
    )
    
    application.add_handler(
    CommandHandler(
        "trash",
        trash_command,
        filters=allowed_users_filter,
    )
)
    application.add_handler(
        CommandHandler(
            "past",
            past_command,
            filters=allowed_users_filter,
        )
    )

    application.add_handler(
        CommandHandler(
            "before",
            before_command,
            filters=allowed_users_filter,
        )
    )

    application.add_handler(
        CommandHandler(
            "stop",
            stop_command,
            filters=allowed_users_filter,
        )
    )
    application.add_error_handler(error_handler)

    if application.job_queue is None:
        raise RuntimeError(
            "JobQueue недоступен. Установите библиотеку командой: "
            'pip install "python-telegram-bot[job-queue]>=22.1,<23.0"'
        )

    application.job_queue.run_repeating(
        check_today_file_job,
        interval=check_interval_seconds,
        first=10,
        name="check_today_json",
    )

    logger.info(
        "Бот запущен. Проверка файла каждые %s секунд.",
        check_interval_seconds,
    )

    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
