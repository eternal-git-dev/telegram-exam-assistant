from aiogram.types import Message, CallbackQuery
from datetime import datetime, timedelta
from core.config import Registration
from database.models import Order
from core.config import settings


def check_deadline(deadline_str: str, min_days: int = 3) -> bool:
    try:
        dl = datetime.strptime(deadline_str.strip(), "%Y-%m-%d %H:%M")
    except Exception:
        return False
    return dl >= (datetime.now() + timedelta(days=min_days))


def set_order(order: Order):
    order.deadline = Registration.deadline
    order.id_subject = Registration.subject
    order.id_type_work = Registration.type_work
    order.id_user = Registration.user_id


def is_admin(user_id):
    return user_id in settings.ADMIN_IDS


def parse_reply(message: CallbackQuery | Message | None, split_number: int | None = 1):
    if message is None:
        return None

    try:
        if isinstance(message, CallbackQuery):
            res = message.data.split(':')[1] if message.data and ':' in message.data else None
        elif isinstance(message, Message):
            parts = message.text.split(maxsplit=split_number)
            res = parts[1] if len(parts) > 1 else None
        else:
            return None

        return int(res) if res else None
    except TypeError:
        return res
    except IndexError:
        return None
    except ValueError:
        return res
