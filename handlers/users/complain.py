from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Command
from emoji import emojize

from keyboards.inline.gaming_keyboards import complain_keyboard, profile_action_target_keyboard
from loader import db, dp
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

    language = user.language

    # Если пользователь нажал "Пожаловаться", не просматривая анкеты
    if profiles is None:
        # Если текущий язык пользователя Русский
        if language == '🇷🇺 Русский':
            await message.answer('Жалобу можно оставить только при просмотре анкеты')

        # Если текущий язык пользователя Английский
        else:
            await message.answer('You can leave a complaint only when viewing the profile')

    # Если пользователь нажал "Пожаловаться", просматривая анкеты
    else:
        if language == '🇷🇺 Русский':
            await message.answer(f'Укажите причину жалобы:\n\n'
                                 f'1. {emojize(":no_one_under_eighteen:")} Материал для взрослых\n'
                                 f'2. {emojize(":shopping_cart:")} Продажа товаров и услуг\n'
                                 f'3. {emojize(":muted_speaker:")} Не отвечает\n'
                                 f'4. {emojize(":red_question_mark:")} Другое\n'
                                 f'5. {emojize(":multiply:")} Отмена\n', reply_markup=complain_keyboard)

        else:
            await message.answer(f'Specify the reason for the complaint:\n\n'
                                 f'1. {emojize(":no_one_under_eighteen:")} Adult material\n'
                                 f'2. {emojize(":shopping_cart:")} Sale of goods and services\n'
                                 f'3. {emojize(":muted_speaker:")} Not responding\n'
                                 f'4. {emojize(":red_question_mark:")} Other\n'
                                 f'5. {emojize(":multiply:")} Cancel\n', reply_markup=complain_keyboard)

        await state.set_state('reason_complaint')


# Сюда попадаем, когда пользователь выбрал причину жалобы
@dp.message_handler(state='reason_complaint')
async def reason_complaint_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user: models.User = data.get('user_')
    language = user.language
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

        if language == '🇷🇺 Русский':
            await message.answer(f'Ваша жалоба принята.\n\n'
                                 f'Жалоба: <b>Материал для взрослых</b>\n\n'
                                 f'Пользователь: <b>{current_profile.name}, {current_profile.age}</b>')
        else:
            await message.answer(f'Your complaint has been accepted.\n\n'
                                 f'Complaint: <b>Adult material</b>\n\n'
                                 f'User: <b>{current_profile.name}, {current_profile.age}</b>')

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
            if language == '🇷🇺 Русский':
                await message.answer('К сожалению, профили, подходящие под ваши критерии поиска, закончились!\n'
                                     'Попробуйте возобновить поиск позднее или измените критерии поиска.')

            else:
                await message.answer('Unfortunately, the profiles that fit your search criteria are over!\n'
                                     'Try resuming the search later or change the search criteria.')

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

        if language == '🇷🇺 Русский':
            await message.answer(f'Ваша жалоба принята.\n\n'
                                 f'Жалоба: <b>Продажа товаров и услуг</b>\n\n'
                                 f'Пользователь: <b>{current_profile.name}, {current_profile.age}</b>')
        else:
            await message.answer(f'Your complaint has been accepted.\n\n'
                                 f'Complaint: <b>Sale of goods and services</b>\n\n'
                                 f'User: <b>{current_profile.name}, {current_profile.age}</b>')

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
            if language == '🇷🇺 Русский':
                await message.answer('К сожалению, профили, подходящие под ваши критерии поиска, закончились!\n'
                                     'Попробуйте возобновить поиск позднее или измените критерии поиска.')

            else:
                await message.answer('Unfortunately, the profiles that fit your search criteria are over!\n'
                                     'Try resuming the search later or change the search criteria.')

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

        if language == '🇷🇺 Русский':
            await message.answer(f'Ваша жалоба принята.\n\n'
                                 f'Жалоба: <b>Не отвечает</b>\n\n'
                                 f'Пользователь: <b>{current_profile.name}, {current_profile.age}</b>')
        else:
            await message.answer(f'Your complaint has been accepted.\n\n'
                                 f'Complaint: <b>Not responding</b>\n\n'
                                 f'User: <b>{current_profile.name}, {current_profile.age}</b>')

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
            if language == '🇷🇺 Русский':
                await message.answer('К сожалению, профили, подходящие под ваши критерии поиска, закончились!\n'
                                     'Попробуйте возобновить поиск позднее или измените критерии поиска.')

            else:
                await message.answer('Unfortunately, the profiles that fit your search criteria are over!\n'
                                     'Try resuming the search later or change the search criteria.')

            await state.reset_state()

    # Пользователь указал причину жалобы "Другое"
    elif option == '❓ 4':

        if language == '🇷🇺 Русский':
            await message.answer('Напишите причину жалобы')
        else:
            await message.answer('Write the reason for the complaint')

        await state.set_state('other_complaint')

    # Пользователь нажал "Отмена"
    elif option == '✖️ 5':
        caption = f'{current_profile.name}, {current_profile.age} - {current_profile.about_yourself}'
        await message.answer_photo(photo=current_profile.photo, caption=caption,
                                   reply_markup=profile_action_target_keyboard)

        await state.set_state('find_profiles')

    # Пользователь написал сообщение (не нажал ни одну из кнопок)
    else:
        await message.answer('Не знаю такой символ')


# Получаем причину жалобы от пользователя, когда он выбрал вариант "Другое"
@dp.message_handler(state='other_complaint')
async def get_other_complaint(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user: models.User = data.get('user_')
    language = user.language
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

    if language == '🇷🇺 Русский':
        await message.answer(f'Ваша жалоба принята.\n\n'
                             f'Жалоба: <b>{reason_complaint}</b>\n\n'
                             f'Пользователь: <b>{current_profile.name}, {current_profile.age}</b>')
    else:
        await message.answer(f'Your complaint has been accepted.\n\n'
                             f'Complaint: <b>{reason_complaint}</b>\n\n'
                             f'User: <b>{current_profile.name}, {current_profile.age}</b>')

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
        if language == '🇷🇺 Русский':
            await message.answer('К сожалению, профили, подходящие под ваши критерии поиска, закончились!\n'
                                 'Попробуйте возобновить поиск позднее или измените критерии поиска.')

        else:
            await message.answer('Unfortunately, the profiles that fit your search criteria are over!\n'
                                 'Try resuming the search later or change the search criteria.')

        await state.reset_state()
