import os
from typing import List
from aiogram.fsm.state import State, StatesGroup
from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import datetime


file_path = os.path.abspath(__file__)
root_path = os.path.dirname((os.path.dirname(file_path)))


class Registration(StatesGroup):
    user_id = State()
    university = State()
    subject = State()
    type_work = State()
    deadline = State()


class Subject(StatesGroup):
    subject = State()
    university = State()

class Typework(StatesGroup):
    typework_name = State()
    subject_id = State()

class Settings(BaseSettings):
    BOT_TOKEN: str

    ADMIN_IDS: List[int]

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 1
    REDIS_PASSWORD: str | None = None
    REDIS_DECODE_RESPONSES: bool = False
    REDIS_MAX_CONNECTIONS: int = 10


    @property
    def DATABASE_URL_asyncpg(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_URL_psycopg(self) -> str:
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(
        env_file=f"{root_path}\.env",
        case_sensitive=False
    )

settings = Settings()

current_datetime = datetime.now()
command_pattern = r"^()"
order_available_status = ["В ожидании", "Завершен", "Отменен"]
data_available_status = ['subjects', 'typeworks', 'universities']
admin_commands = [f'/view_orders  - Вывести список заказов по статусу.',
                  '/view_data - Вывести список данных по типу',
                  '/ban [id пользователя] - забанить пользователя по его id',
                  '/unban [id пользователя] - разбанить пользователя по его id',
                  '/check [id пользователя] - вывести все имеющиеся заявки на конкретного пользователя',
                  '/add_subject [Название предмета] - добавить предмет в бд для конкретного вуза. Вводить параметры через пробел.',
                  '/dell_subject [Название предмета] - удалить предмет из бд для конкретного вуза. Вводить параметры через пробел.',
                  '/add_typework [название типа работы] - добавить предмет в бд.',
                  '/dell_typework [название типа работы] - удалить тип работы.',
                  '/info [id пользователя] - вывести информацию о пользователе.']
