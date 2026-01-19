from sqlalchemy.exc import SQLAlchemyError

from database.models import async_session
from database.requests import (
    add_subject, add_type, dell_subject,
    get_typework, remove_association)
from enums import OperationResult, AdminDataType
from database.requests import get_universities, get_subjects, get_typeworks


DATA_MAP = {
    AdminDataType.UNIVERSITIES: get_universities,
    AdminDataType.SUBJECTS: get_subjects,
    AdminDataType.TYPEWORKS: get_typeworks,
}


async def add_subject_to_university(subject_name: str, university_id: int):
    async with async_session() as session:
        op_status = await add_subject(session, subject_name, university_id)
        if op_status == OperationResult.SUCCESS:
            await session.commit()
        return op_status


async def add_typework_for_subject(typework_name: str, subject_id: int):
    async with async_session() as session:
        op_result = await add_type(session, typework_name, subject_id)
        if op_result == OperationResult.SUCCESS:
            await session.commit()
        return op_result


async def dell_subject_by_name(subject_name: str, university_id: int):
    async with async_session() as session:
        op_result = await dell_subject(session, subject_name, university_id)
        if op_result == OperationResult.SUCCESS:
            await session.commit()
        return op_result

async def dell_typework_by_name(typework_name: str, subject_id: int):
    async with async_session() as session:
        op_result, typework = await get_typework(session, typework_name)
        if op_result is not OperationResult.SUCCESS:
            return op_result

        op_result, status = await remove_association(session=session, typework_id=typework.id, subject_id=subject_id)

        if op_result is not OperationResult.SUCCESS:
            await session.rollback()
            return op_result

        await session.commit()
        return op_result


async def fetch_reference_data(data_type: AdminDataType):
    if data_type not in DATA_MAP:
        raise ValueError("Unknown data type")

    repo_fn = DATA_MAP[data_type]

    async with async_session() as session:
        try:
            items = await repo_fn(session)
        except SQLAlchemyError as exc:
            print(exc)
            raise

    if not items:
        return []
    return items