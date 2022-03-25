from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Command

from keyboards.inline.gaming_keyboards import complain_keyboard, profile_action_target_keyboard
from loader import db, dp, _
from utils.db_api import models


# Сюда попадаем, когда пользователь нажал "Пожаловаться"(/complain)
@dp.message_handler(Command(['complain']), state='*')
async def command_complain(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user: models.User = data.get('user_')
    profiles = data.get('profiles')

    if user is None:
        user_id = message.from_user.id
        user: models.User = await db.get_user(user_id)
        await state.update_data(user_=user)

    # Если пользователь нажал "Пожаловаться", не просматривая анкеты
    if profiles is None:
        await message.answer(_('Жалобу можно оставить только при просмотре анкеты'))

    # Если пользователь нажал "Пожаловаться", просматривая анкеты
    else:
        await message.answer(_('Укажите причину жалобы:\n\n'
                               '1. 🔞 Материал для взрослых\n'
                               '2. 🛒 Продажа товаров и услуг\n'
                               '3. 🔇 Не отвечает\n'
                               '4. ❓ Другое\n'
                               '5. ✖️ Отмена\n'), reply_markup=complain_keyboard)

        await state.set_state('reason_complaint')


# Сюда попадаем, когда пользователь выбрал причину жалобы
@dp.message_handler(state='reason_complaint')
async def reason_complaint_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user: models.User = data.get('user_')
    profiles = data.get('profiles')
    count_profiles = data.get('count_profiles')
    current_profile_number = data.get('current_profile_number')
    current_profile: models.User = profiles[current_profile_number]

    option = message.text

    # Пользователь указал причину жалобы "Материал для взрослых"
    if option == '🔞 1':
        reason_complaint = 'Материал для взрослых'

        # Получаем количество жалоб на профиль
        complaint = await db.get_user_complaints(current_profile.user_id)

        # Если количество жалоб меньше 3, то прибавляем еще одну жалобу
        if complaint + 1 < 3:
            complaint += 1
            await current_profile.update(complaint=complaint).apply()

            # Добавляем в БД причину жалобы
            await db.add_complaint_for_profile(complaint_profile_id=current_profile.user_id,
                                               reason_complaint=reason_complaint)

        # Если количество жалоб на профиль равно 3, то блокируем профиль
        else:
            complaint += 1
            await current_profile.update(complaint=complaint, enable=False).apply()

            # Добавляем в БД причину жалобы
            await db.add_complaint_for_profile(complaint_profile_id=current_profile.user_id,
                                               reason_complaint=reason_complaint)

        text = _('Ваша жалоба принята.\n\n'
                 'Жалоба: <b>Материал для взрослых</b>\n\n'
                 'Пользователь: <b>{current_profile_name}, {current_profile_age}</b>').format(
            current_profile_name=current_profile.name, current_profile_age=current_profile.age)
        await message.answer(text)

        # Проверяем, есть ли еще анкеты для показа
        if current_profile_number + 1 < count_profiles:
            next_profile_number = current_profile_number + 1
            next_profile: models.User = profiles[next_profile_number]

            caption = f'{next_profile.name}, {next_profile.age} - {next_profile.about_yourself}'
            await message.answer_photo(photo=next_profile.photo, caption=caption,
                                       reply_markup=profile_action_target_keyboard)

            await state.update_data(current_profile_number=next_profile_number)

            await state.set_state('find_profiles')

        # Если закончились анкеты
        else:
            await message.answer(_('К сожалению, профили, подходящие под ваши критерии поиска, закончились!\n'
                                   'Попробуйте возобновить поиск позднее или измените критерии поиска.'))

            await state.reset_state()

    # Пользователь указал причину жалобы "Продажа товаров и услуг"
    elif option == '🛒 2':
        reason_complaint = 'Продажа товаров и услуг'

        # Получаем количество жалоб на профиль
        complaint = await db.get_user_complaints(current_profile.user_id)

        # Если количество жалоб меньше 3, то прибавляем еще одну жалобу
        if complaint + 1 < 3:
            complaint += 1
            await current_profile.update(complaint=complaint).apply()

            # Добавляем в БД причину жалобы
            await db.add_complaint_for_profile(complaint_profile_id=current_profile.user_id,
                                               reason_complaint=reason_complaint)

        # Если количество жалоб на профиль равно 3, то блокируем профиль
        else:
            complaint += 1
            await current_profile.update(complaint=complaint, enable=False).apply()

            # Добавляем в БД причину жалобы
            await db.add_complaint_for_profile(complaint_profile_id=current_profile.user_id,
                                               reason_complaint=reason_complaint)

        text = _('Ваша жалоба принята.\n\n'
                 'Жалоба: <b>Материал для взрослых</b>\n\n'
                 'Пользователь: <b>{current_profile_name}, {current_profile_age}</b>').format(
            current_profile_name=current_profile.name, current_profile_age=current_profile.age)
        await message.answer(text)

        # Проверяем, есть ли еще анкеты для показа
        if current_profile_number + 1 < count_profiles:
            next_profile_number = current_profile_number + 1
            next_profile: models.User = profiles[next_profile_number]

            caption = f'{next_profile.name}, {next_profile.age} - {next_profile.about_yourself}'
            await message.answer_photo(photo=next_profile.photo, caption=caption,
                                       reply_markup=profile_action_target_keyboard)

            await state.update_data(current_profile_number=next_profile_number)

            await state.set_state('find_profiles')

        # Если закончились анкеты
        else:
            await message.answer(_('К сожалению, профили, подходящие под ваши критерии поиска, закончились!\n'
                                   'Попробуйте возобновить поиск позднее или измените критерии поиска.'))

            await state.reset_state()

    # Пользователь указал причину жалобы "Не отвечает"
    elif option == '🔇 3':
        reason_complaint = 'Не отвечает'

        # Получаем количество жалоб на профиль
        complaint = await db.get_user_complaints(current_profile.user_id)

        # Если количество жалоб меньше 3, то прибавляем еще одну жалобу
        if complaint + 1 < 3:
            complaint += 1
            await current_profile.update(complaint=complaint).apply()

            # Добавляем в БД причину жалобы
            await db.add_complaint_for_profile(complaint_profile_id=current_profile.user_id,
                                               reason_complaint=reason_complaint)

        # Если количество жалоб на профиль равно 3, то блокируем профиль
        else:
            complaint += 1
            await current_profile.update(complaint=complaint, enable=False).apply()

            # Добавляем в БД причину жалобы
            await db.add_complaint_for_profile(complaint_profile_id=current_profile.user_id,
                                               reason_complaint=reason_complaint)

        text = _('Ваша жалоба принята.\n\n'
                 'Жалоба: <b>Материал для взрослых</b>\n\n'
                 'Пользователь: <b>{current_profile_name}, {current_profile_age}</b>').format(
            current_profile_name=current_profile.name, current_profile_age=current_profile.age)
        await message.answer(text)

        # Проверяем, есть ли еще анкеты для показа
        if current_profile_number + 1 < count_profiles:
            next_profile_number = current_profile_number + 1
            next_profile: models.User = profiles[next_profile_number]

            caption = f'{next_profile.name}, {next_profile.age} - {next_profile.about_yourself}'
            await message.answer_photo(photo=next_profile.photo, caption=caption,
                                       reply_markup=profile_action_target_keyboard)

            await state.update_data(current_profile_number=next_profile_number)

            await state.set_state('find_profiles')

        # Если закончились анкеты
        else:
            await message.answer(_('К сожалению, профили, подходящие под ваши критерии поиска, закончились!\n'
                                   'Попробуйте возобновить поиск позднее или измените критерии поиска.'))

            await state.reset_state()

    # Пользователь указал причину жалобы "Другое"
    elif option == '❓ 4':

        await message.answer(_('Напишите причину жалобы'))
        await state.set_state('other_complaint')

    # Пользователь нажал "Отмена"
    elif option == '✖️ 5':
        caption = f'{current_profile.name}, {current_profile.age} - {current_profile.about_yourself}'
        await message.answer_photo(photo=current_profile.photo, caption=caption,
                                   reply_markup=profile_action_target_keyboard)

        await state.set_state('find_profiles')

    # Пользователь написал сообщение (не нажал ни одну из кнопок)
    else:
        await message.answer(_('Не знаю такой символ'))


# Получаем причину жалобы от пользователя, когда он выбрал вариант "Другое"
@dp.message_handler(state='other_complaint')
async def get_other_complaint(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user: models.User = data.get('user_')
    profiles = data.get('profiles')
    count_profiles = data.get('count_profiles')
    current_profile_number = data.get('current_profile_number')
    current_profile: models.User = profiles[current_profile_number]

    reason_complaint = message.text

    # Получаем количество жалоб на профиль
    complaint = await db.get_user_complaints(current_profile.user_id)

    # Если количество жалоб меньше 3, то прибавляем еще одну жалобу
    if complaint + 1 < 3:
        complaint += 1
        await current_profile.update(complaint=complaint).apply()

        # Добавляем в БД причину жалобы
        await db.add_complaint_for_profile(complaint_profile_id=current_profile.user_id,
                                           reason_complaint=reason_complaint)

    # Если количество жалоб на профиль равно 3, то блокируем профиль
    else:
        complaint += 1
        await current_profile.update(complaint=complaint, enable=False).apply()

        # Добавляем в БД причину жалобы
        await db.add_complaint_for_profile(complaint_profile_id=current_profile.user_id,
                                           reason_complaint=reason_complaint)

    text = _('Ваша жалоба принята.\n\n'
             'Жалоба: <b>{reason_complaint}</b>\n\n'
             'Пользователь: <b>{current_profile_name}, {current_profile_age}</b>').format(
        reason_complaint=reason_complaint, current_profile_name=current_profile.name,
        current_profile_age=current_profile.age)
    await message.answer(text)

    # Проверяем, есть ли еще анкеты для показа
    if current_profile_number + 1 < count_profiles:
        next_profile_number = current_profile_number + 1
        next_profile: models.User = profiles[next_profile_number]

        caption = f'{next_profile.name}, {next_profile.age} - {next_profile.about_yourself}'
        await message.answer_photo(photo=next_profile.photo, caption=caption,
                                   reply_markup=profile_action_target_keyboard)

        await state.update_data(current_profile_number=next_profile_number)

        await state.set_state('find_profiles')

    # Если закончились анкеты
    else:
        await message.answer(_('К сожалению, профили, подходящие под ваши критерии поиска, закончились!\n'
                               'Попробуйте возобновить поиск позднее или измените критерии поиска.'))

        await state.reset_state()
