from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.filters import Command
from middlewares import AdminMiddleWare
from services.orders_service import OrderService
from core.config import Typework, Subject
from utils import parse_reply

from enums import OperationResult, AdminDataType

from keyboards.admin_keyboards import dell_university, dell_subjects, add_university, add_subjects, type_works, get_data_keyboard
from keyboards.common_keyboards import get_global_keyboard
from services.admin_service import (
    add_subject_to_university, add_typework_for_subject,
    dell_subject_by_name, dell_typework_by_name,
    fetch_reference_data)
from services.user_service import ban_user_service, unban_user_service, user_info
from services.notifications_service import NotificationsService


admin_router = Router()
admin_router.message.middleware(AdminMiddleWare())

order_service = OrderService()
notify = NotificationsService()


@admin_router.message(Command('add_subject'))
async def add_subject_handler(message: Message, state: FSMContext):
    command_parts = parse_reply(message)
    if len(command_parts) < 2:
        await message.answer('Нужно указать название нового предмета')
        return
    await state.set_state(Subject.subject)
    subject_name = command_parts[1]
    await state.update_data(subject=subject_name)
    await state.set_state(Subject.university)
    await message.answer('Выбери университет:', reply_markup=await add_university())



@admin_router.callback_query(F.data.startswith('add_univers:'))
async def get_university_for_subject_callback(callback: CallbackQuery, state: FSMContext):
    university_id = parse_reply(callback)
    await state.update_data(university=university_id)
    data = await state.get_data()

    try:
        subject_name = data.get("subject")
        university_id = data.get("university")
        add_status = await add_subject_to_university(subject_name, university_id)

        if add_status == OperationResult.SUCCESS:
            await callback.message.edit_text(f'Предмет {subject_name} успешно добавлен.')
            return await state.clear()
        if add_status == OperationResult.EXISTS:
            await callback.message.edit_text('Такой предмет для данной платформы уже существует!')
        if add_status == OperationResult.UNKNOWN_ERROR:
            await callback.message.edit_text(f'Неизвестная ошибка при добавлении предмета.')
    except Exception as e:
        print(e)
        await callback.message.edit_text("Произошла ошибка при обработке данных. Попробуй позже.")


@admin_router.callback_query(F.data.startswith('add_subject:'))
async def get_subject_for_typework_callback(callback: CallbackQuery, state: FSMContext):

    subject = parse_reply(callback)
    await state.update_data(subject_id=subject)
    data = await state.get_data()

    try:
        typework = data.get("typework_name")
        subject = data.get("subject_id")
        op_result = await add_typework_for_subject(typework_name=typework, subject_id=subject)

        if op_result == OperationResult.NOT_FOUND:
            return await callback.message.edit_text('Такой тип занятия для данного предмета уже существует!')
        if op_result == OperationResult.FAILED:
            return await callback.message.edit_text('Не удалось занятие к данному предмету тип занятия!')
        if op_result == OperationResult.SUCCESS:
            await callback.message.edit_text(f'Тип занятия {typework} успешно добавлен.')
            return await state.clear()
    except Exception as e:
        print(e)
        await callback.message.edit_text("Произошла ошибка при обработке данных. Попробуй позже.")


@admin_router.message(Command('add_typework'))
async def add_typework(message: Message, state: FSMContext):
    command_parts = parse_reply(message)
    if len(command_parts) < 2:
        await message.answer(
            'Необходимо ввести название нового типа занятия!')
        return
    typework = command_parts[1]
    await state.set_state(Typework.typework_name)
    await state.update_data(typework_name=typework)
    await state.set_state(Typework.subject_id)
    await message.answer('Выбери университет', reply_markup=await add_subjects())


@admin_router.message(Command('dell_subject'))
async def delete_subject(message: Message, state: FSMContext):
    command_parts = parse_reply(message)
    if len(command_parts) < 2:
        await message.answer(f'Нужно указать название предмета, который нужно удалить')
        return
    await state.set_state(Subject.subject)
    subject_name = command_parts[1]
    await state.update_data(subject=subject_name)
    await state.set_state(Subject.university)
    await message.answer('Выбери университет, для которого нужно удалить предмет.', reply_markup=await dell_university())


@admin_router.callback_query(F.data.startswith('dell_univers:'))
async def get_university_for_del_subject_callback(callback: CallbackQuery, state: FSMContext):
    university_id = parse_reply(callback)
    await state.update_data(university=university_id)
    data = await state.get_data()
    try:
        subject_name = data.get("subject")
        university_id = data.get("university")
        op_result = await dell_subject_by_name(subject_name=subject_name,university_id=university_id)
        if op_result == OperationResult.NOT_FOUND:
            return await callback.message.edit_text('Такого предмета не существует для данного вуза!')
        if op_result == OperationResult.SUCCESS:
            return await callback.message.edit_text(f'Предмет {subject_name} успешно удален.')

    except Exception as e:
        print(e)
        await callback.message.edit_text("Произошла ошибка при обработке данных. Попробуй позже.")


@admin_router.message(Command('dell_typework'))
async def dell_typework(message: Message, state: FSMContext):
    command_parts = parse_reply(message)
    if len(command_parts) < 2:
        await message.answer('Необходимо ввести полное название типа занятия!')
        return
    await state.set_state(Typework.typework_name)
    typework = command_parts[1]
    await state.update_data(typework_name=typework)
    await state.set_state(Typework.subject_id)
    await message.answer('Выбери предмет, у которого нужно удалить этот тип занятия:',reply_markup=await dell_subjects())


@admin_router.callback_query(F.data.startswith('dell_subject:'))
async def get_subject_for_del_typework_callback(callback: CallbackQuery, state: FSMContext):
    try:
        subject_id = parse_reply(callback)
        await state.update_data(subject_id=subject_id)
        data = await state.get_data()
        typework = data.get("typework_name")
        op_result = await dell_typework_by_name(typework_name=typework,subject_id=subject_id)
        if op_result == OperationResult.NOT_FOUND:
            return await callback.message.edit_text('Такого типа занятия не существует')
        if op_result == OperationResult.SUCCESS:
            return await callback.message.edit_text(f'Тип занятия {typework} успешно удален')
        if op_result == OperationResult.UNKNOWN_ERROR:
            return await callback.message.edit_text(f"Ошибка при добавлении.")
    except Exception as e:
        print(e)
        await callback.message.edit_text("Произошла ошибка при обработке данных. Попробуй позже.")


@admin_router.message(Command('view_orders'))
async def view_orders(message: Message):
    print(1)
    typeworks_keyboard = await type_works()
    await message.answer(text=f"Список доступных типов",
                         reply_markup=typeworks_keyboard)


@admin_router.message(Command('view_data'))
async def view_data(message: Message):
    await message.answer(f'Доступные данные:', reply_markup=get_data_keyboard())


@admin_router.message(F.text == 'Университеты')
async def universities(message: Message):
    try:
        items = await fetch_reference_data(AdminDataType.UNIVERSITIES)
    except Exception:
        await message.answer("Ошибка доступа к БД, попробуйте позже")
        return

    if not items:
        await message.answer("Записей не найдено.")
        return
    lines = []
    for it in items:
        lines.append(f"{getattr(it, 'id', '?')}: {getattr(it, 'name', '-')}")
    text = "\n".join(lines)
    await message.answer(text)

@admin_router.message(F.text == 'Предметы')
async def subjects(message: Message):
    try:
        items = await fetch_reference_data(AdminDataType.SUBJECTS)
    except Exception:
        await message.answer("Ошибка доступа к БД, попробуйте позже")
        return

    if not items:
        await message.answer("Записей не найдено.")
        return
    lines = []
    for it in items:
        lines.append(f"{getattr(it, 'id', '?')}: {getattr(it, 'name', '-')}")
    text = "\n".join(lines)
    await message.answer(text)


@admin_router.message(F.text == 'Типы работ')
async def subjects(message: Message):
    try:
        items = await fetch_reference_data(AdminDataType.TYPEWORKS)
    except Exception:
        await message.answer("Ошибка доступа к БД, попробуйте позже")
        return

    if not items:
        await message.answer("Записей не найдено.")
        return
    lines = []
    for it in items:
        lines.append(f"{getattr(it, 'id', '?')}: {getattr(it, 'name', '-')}")
    text = "\n".join(lines)
    await message.answer(text)


@admin_router.callback_query(F.data.startswith('view_data_type'))
async def data_types(callback: CallbackQuery):
    data_type = parse_reply(callback)
    orders = await order_service.get_orders_by_status(status=data_type)
    if orders is None:
        return await callback.message.answer(f'Для статуса {data_type} нет заявок для отображения')
    msg = await order_service.print_orders(orders)
    await callback.message.answer('\n'.join(msg))


@admin_router.message(Command('ban'))
async def ban(message: Message):
    id_user = parse_reply(message)
    if not id_user:
        await message.answer('Необходимо ввести id пользователя!')
        return

    ban_status = await ban_user_service(id_user)

    if ban_status == OperationResult.NOT_FOUND:
        return await message.answer("Пользователь не найден")

    if ban_status == OperationResult.UNKNOWN_ERROR:
        return await message.answer("Ошибка во время выполнения команды")

    if ban_status:
        return await message.answer("Пользователь успешно забанен")


@admin_router.message(Command('unban'))
async def unban(message: Message):
    id_user = parse_reply(message)
    if not id_user:
        await message.answer('Необходимо ввести id пользователя!')
        return

    unban_status = await unban_user_service(id_user)
    if unban_status == OperationResult.NOT_FOUND:
        return await message.answer("Пользователь не найден")
    if unban_status == OperationResult.SUCCESS:
        return await message.answer("Пользователь успешно разбанен")
    if unban_status == OperationResult.UNKNOWN_ERROR:
        return await message.answer("Ошибка во время выполнения команды")


@admin_router.message(Command('check'))
async def check_user(message: Message):
    command_parts = parse_reply(message)
    if len(command_parts) < 2:
        await message.answer('Необходимо ввести id пользователя!')
        return
    try:
        id_user = int(command_parts[1])
        orders = await order_service.get_orders_for_display(id_user=id_user)
        msg = order_service.format_orders_list(orders)
        await message.answer('\n'.join(msg))
    except (ValueError, TypeError):
        await message.answer('Необходиомо ввести id пользователя!')



@admin_router.message(Command('info'))
async def get_information(message: Message):
        user_id = parse_reply(message)
        if user_id is None:
            return await message.answer('Необходимо ввести id пользователя!')
        user = await user_info(user_id)
        if user is None:
            await message.answer('Пользователя с таким id не существует!')
            return
        await message.answer(f'Id пользователя: {user.id}\nИмя пользователя: {user.fullname}\nНик пользователя: @{user.nickname}')


@admin_router.message(Command('send_message'))
async def send_message(message: Message):
    command_parts = parse_reply(message, split_number=2)
    if len(command_parts) < 2:
        await message.answer('Необходимо ввести сообщене!')
    text = ' '.join(command_parts[2:])
    try:
        user_id = int(command_parts[1])
    except ValueError:
        return await message.answer('Некорректный id пользователя')

    send_status = await notify.send_message_by_tg_id(
        bot=message.bot,
        receiver_id=user_id,
        text=text
    )
    if send_status:
        return await message.answer('Сообщение успешно отправлено!')
    return await message.answer('Ошибка при отправке сообщения')


@admin_router.callback_query(F.data.startswith('contact:'))
async def send_contact(callback: CallbackQuery):
    user_id = parse_reply(callback)
    user= await user_info(user_id)
    if user is None:
        return await callback.message.answer("Пользователь не найден")

    nickname = user.get("nickname", "No nickname")
    fullname = user.get("fullname", "No fullname")

    await callback.message.answer(f"Id пользователя: {user_id}\nНик пользователя: @{nickname}\nИмя пользователя: {fullname}")


@admin_router.callback_query(F.data.startswith('cancel_order:'))
async def cancel_order(callback: CallbackQuery):
    order_id = await order_service.cancel_order_by_id(callback)
    if order_id:
        await callback.message.answer(f'Ордер #{order_id} успешно отменен')
    else:
        await callback.message.answer(f'Ошибка при отмене ордера')


@admin_router.callback_query(F.data.startswith('accept_order:'))
async def accept_order(callback: CallbackQuery):
    order_id = await order_service.complete_order_by_id(callback)
    if order_id:
        await callback.message.answer(f'Ордер #{order_id} успешно завершен')
    else:
        await callback.message.answer(f'Ошибка при завершении ордера')


@admin_router.callback_query(F.data.startswith('to_main'))
async def go_to_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except:
        pass
    await callback.message.answer("Заполнение формы отменено.", reply_markup=get_global_keyboard())
