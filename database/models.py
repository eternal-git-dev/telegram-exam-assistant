import datetime
from sqlalchemy import String, ForeignKey, Boolean, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from typing import List, Annotated
from enums import OrderStatus
from core.config import settings
from sqlalchemy import Integer, Identity, BigInteger


engine = create_async_engine(url=settings.DATABASE_URL_asyncpg)
async_session = async_sessionmaker(engine)


intpk = Annotated[
    int,
    mapped_column(
        Integer,
        Identity(always=True),
        primary_key=True
    )
]


class Base(AsyncAttrs, DeclarativeBase):
    pass


subject_typework_association = Table(
    'subject_typework_association',
    Base.metadata,
    Column('subject_id', ForeignKey('subjects.id'), primary_key=True),
    Column('typework_id', ForeignKey('typeworks.id'), primary_key=True)
)


class Subject(Base):
    __tablename__ = 'subjects'

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(45))
    university_id: Mapped[int] = mapped_column(ForeignKey('universities.id'))

    typeworks: Mapped[List["TypeWork"]] = relationship(
        "TypeWork",
        secondary=subject_typework_association,
        back_populates="subjects",
        lazy="selectin"
    )


class TypeWork(Base):
    __tablename__ = 'typeworks'

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(35))

    subjects: Mapped[List["Subject"]] = relationship(
        "Subject",
        secondary=subject_typework_association,
        back_populates="typeworks",
        lazy="selectin"
    )


class User(Base):
    __tablename__ = 'users'

    id: Mapped[intpk]
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    banned: Mapped[bool] = mapped_column(Boolean, default=False)
    nickname: Mapped[str] = mapped_column(String(100))
    fullname: Mapped[str] = mapped_column(String(100))


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[intpk]
    id_user: Mapped[BigInteger] = mapped_column(ForeignKey('users.id'), nullable=False)
    id_university: Mapped[int] = mapped_column(ForeignKey('universities.id'), nullable=False)
    id_subject: Mapped[int] = mapped_column(ForeignKey('subjects.id'), nullable=False)
    id_type_work: Mapped[int] = mapped_column(ForeignKey('typeworks.id'))
    deadline: Mapped[datetime.datetime]
    status: Mapped[OrderStatus] = mapped_column(default=OrderStatus.PENDING)

    university = relationship("University", lazy="joined")
    subject = relationship("Subject", lazy="joined")
    type_work = relationship("TypeWork", lazy="joined")
    user = relationship("User", lazy="joined")


class University(Base):
    __tablename__ = 'universities'

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(45))


async def async_main():

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)