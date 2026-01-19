from database.requests import get_subject, get_subject_with_typeworks
from database.models import async_session
from enums import OperationResult


async def get_subjects_by_university_id(university_id: int):
    try:
        async with async_session() as session:
            op_result, subjects = await get_subject(session=session, university_id=university_id)
            if op_result == OperationResult.SUCCESS:
                return subjects
            return None
    except Exception as e:
        print(e)
        return None


async def get_typeworks_for_subject(subject_id: int):
    try:
        async with async_session() as session:
            op_result, subjects = await get_subject_with_typeworks(session=session, subject_id=subject_id)
            if op_result == OperationResult.SUCCESS:
                return subjects
            return None
    except Exception as e:
        print(e)
        return None
