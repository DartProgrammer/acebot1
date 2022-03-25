import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from handlers.users.my_profile import find_query
from keyboards.inline.gaming_keyboards import get_send_message_keyboard, \
    complain_keyboard, profile_action_like_keyboard, action_for_profile
from loader import dp, bot, db, _
from utils.db_api import models
# Если пользователь нажал 👍 (Показать)
from utils.range import async_range


# Здесь ловим действия со стороны пользователя 2, когда пользователь 1 написал письмо


@dp.message_handler(text='👍', state='in_send_message')
async def show_users_profiles(message: types.Message, state: FSMContext):
    data = await state.get_data()

    # Получаем информацию о пользователе, который получил письмо
    second_user_id = message.from_user.id
    second_user: models.User = await db.get_user(second_user_id)
    language_second_user = second_user.language

    # Получаем всех пользователей, которые написали письмо
    all_users_send_message = await db.get_users_send_message(second_user_id)
    current_profile_send_message_number = 0
    count_users_send_message = len(all_users_send_message)
    current_profile: models.User = all_users_send_message[current_profile_send_message_number]

    count_users_send_message_for_text = data.get('count_users_send_message_for_text')
    if count_users_send_message_for_text is None:
        count_users_send_message_for_text = count_users_send_message - 1

    await state.update_data(second_user=second_user,
                            all_users_send_message=all_users_send_message,
                            count_users_send_message=count_users_send_message,
                            current_profile_send_message_number=current_profile_send_message_number,
                            count_users_send_message_for_text=count_users_send_message_for_text - 1)

    photo = current_profile.photo
    game1 = current_profile.game1
    game2 = current_profile.game2

    if game1 is not None and game2 is not None:
        games = f'{game1}, {game2}'
    elif game2 is None:
        games = f'{game1}'
    elif game1 is None:
        games = f'{game2}'
    else:
        games = ''

    # Изменяем текст в зависимости от количества лайков
    if count_users_send_message == 1:
        text = _('Кому-то понравилась твоя анкета:\n\n'
                 '{current_profile.name}, {current_profile.age} из {current_profile.country}\n'
                 'Хобби: <b>{current_profile.hobby}</b>\n'
                 'О себе: <b>{current_profile.about_yourself}</b>\n'
                 'Играет в игры: <b>{games}</b>'
                 'Письмо: <b>{current_profile.send_message_text}</b>').format(current_profile=current_profile,
                                                                              games=games)
    else:
        text = _('Кому-то понравилась твоя анкета (и ещё {count_users_send_message_for_text})\n\n'
                 '{current_profile.name}, {current_profile.age} из {current_profile.country}\n'
                 'Хобби: <b>{current_profile.hobby}</b>\n'
                 'О себе: <b>{current_profile.about_yourself}</b>\n'
                 'Играет в игры: <b>{games}</b>'
                 'Письмо: <b>{current_profile.send_message_text}</b>').format(current_profile=current_profile,
                                                                              count_users_send_message_for_text=count_users_send_message_for_text,
                                                                              games=games)

    # Если пользователь без фото
    if photo == 'None':
        await message.answer(text=text, reply_markup=get_send_message_keyboard())

    # Если пользователь с фото
    else:
        await message.answer_photo(photo=photo, caption=text,
                                   reply_markup=get_send_message_keyboard())


# Если пользователь нажал 💤 (Не хочу больше никого смотреть)
@dp.message_handler(text='💤', state='in_send_message')
async def not_show_users_profiles(message: types.Message, state: FSMContext):
    second_user_id = message.from_user.id
    second_user: models.User = await db.get_user(second_user_id)
    language = second_user.language
    await state.update_data(second_user=second_user)

    text = _('Так ты не узнаешь, что кому-то нравишься... '
             'Точно хочешь отключить свою анкету?\n\n'
             '1. Да, отключить анкету.\n'
             '2. Нет, вернуться назад.')
    await message.answer(text=text, reply_markup=ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(text='1'),
            KeyboardButton(text='2')
        ]
    ], resize_keyboard=True, one_time_keyboard=True))

    await state.set_state('disable_second_profile_send_message')


# Сюда попадаем, когда пользователь нажал "Ответить" или "⚠️ Пожаловаться"
@dp.message_handler(state='in_send_message')
async def answer_message(message: types.Message, state: FSMContext):
    data = await state.get_data()

    # Получаем информацию о пользователе
    second_user: models.User = data.get('second_user')
    user_language = second_user.language

    if message.text in ['Ответить', 'Answer']:
        await message.answer(_('Напишите сообщение, которое хотите отправить'))
        await state.set_state('in_send_message_wait_answer')

    elif message.text in ['⚠️ Пожаловаться', '⚠️ Complain']:
        await message.answer(_('Укажите причину жалобы:\n\n'
                               '1. 🔞 Материал для взрослых\n'
                               '2. 🛒 Продажа товаров и услуг\n'
                               '3. 🔇 Не отвечает\n'
                               '4. ❓ Другое\n'
                               '5. ✖️ Отмена\n'), reply_markup=complain_keyboard)

        await state.set_state('send_message_reason_complaint')


# Сюда попадаем, когда пользователь выбрал причину жалобы
@dp.message_handler(state='send_message_reason_complaint')
async def reason_complaint_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()

    # Получаем информацию о пользователе
    second_user: models.User = data.get('second_user')
    language = second_user.language

    # Получаем данные по найденным профилям
    all_users_send_message = data.get('all_users_send_message')
    count_users_send_message = data.get('count_users_send_message')
    count_users_send_message_for_text = data.get('count_users_send_message_for_text')
    current_profile_number = data.get('current_profile_send_message_number')
    current_profile_send_msg: models.SendMessageProfiles = all_users_send_message[current_profile_number]

    # Устанавливаем у прочитанного сообщение признак "Прочитано"
    await db.setting_the_attribute_read(current_profile_send_msg[0])

    current_profile_user_id = current_profile_send_msg[1]
    current_profile: models.User = await db.get_user(current_profile_user_id)

    option = message.text

    # Пользователь указал причину жалобы "Материал для взрослых"
    if option == '🔞 1':
        reason_complaint = 'Материал для взрослых'

        # Получаем количество жалоб на профиль
        complaint = await db.get_user_complaints(current_profile_user_id)

        # Если количество жалоб меньше 3, то прибавляем еще одну жалобу
        if complaint + 1 < 3:
            complaint += 1
            await current_profile.update(complaint=complaint).apply()

            # Добавляем в БД причину жалобы
            await db.add_complaint_for_profile(complaint_profile_id=current_profile_user_id,
                                               reason_complaint=reason_complaint)

        # Если количество жалоб на профиль равно 3, то блокируем профиль
        else:
            complaint += 1
            await current_profile.update(complaint=complaint, enable=False).apply()

            # Добавляем в БД причину жалобы
            await db.add_complaint_for_profile(complaint_profile_id=current_profile_user_id,
                                               reason_complaint=reason_complaint)

        await message.answer(_('Ваша жалоба принята.\n\n'
                               'Жалоба: <b>Материал для взрослых</b>\n\n'
                               'Пользователь: <b>{current_profile.name}, {current_profile.age}</b>').format(
            current_profile=current_profile))

        # Показываем пользователей, которые написали сообщение
        if current_profile_number + 1 < count_users_send_message:

            # Показываем следующую анкету
            current_profile: models.User = all_users_send_message[current_profile_number + 1]

            photo = current_profile.photo
            game1 = current_profile.game1
            game2 = current_profile.game2

            if game1 is not None and game2 is not None:
                games = f'{game1}, {game2}'
            elif game2 is None:
                games = f'{game1}'
            elif game1 is None:
                games = f'{game2}'
            else:
                games = ''

            # Изменяем текст в зависимости от количества лайков
            if count_users_send_message_for_text == 0:
                text = _('Кому-то понравилась твоя анкета:\n\n'
                         '{current_profile.name}, {current_profile.age} из {current_profile.country}\n'
                         'Хобби: <b>{current_profile.hobby}</b>\n'
                         'О себе: <b>{current_profile.about_yourself}</b>\n'
                         'Играет в игры: <b>{games}</b>'
                         'Письмо: <b>{current_profile.send_message_text}</b>').format(current_profile=current_profile,
                                                                                      games=games)
            else:
                text = _('Кому-то понравилась твоя анкета (и ещё {count_users_send_message_for_text})\n\n'
                         '{current_profile.name}, {current_profile.age} из {current_profile.country}\n'
                         'Хобби: <b>{current_profile.hobby}</b>\n'
                         'О себе: <b>{current_profile.about_yourself}</b>\n'
                         'Играет в игры: <b>{games}</b>'
                         'Письмо: <b>{current_profile.send_message_text}</b>').format(count_users_send_message_for_text,
                                                                                      current_profile, games=games)

            # Если пользователь без фото
            if photo == 'None':
                await message.answer(text=text, reply_markup=get_send_message_keyboard())

            # Если пользователь с фото
            else:
                await message.answer_photo(photo=photo, caption=text,
                                           reply_markup=get_send_message_keyboard())

            await state.update_data(current_profile_send_message_number=current_profile_number + 1,
                                    count_users_send_message_for_text=count_users_send_message_for_text - 1)

            await state.set_state('in_send_message')

        # Сюда попадаем, когда показали всех пользователей, которым понравилась анкета
        else:
            await message.answer(_('Чтобы получать больше лайков ❤️\n'
                                   'Подпишись на канал Ссылка на канал✅'),
                                 reply_markup=ReplyKeyboardMarkup(keyboard=[
                                     [
                                         KeyboardButton(text=_('Продолжить просмотр анкет'))
                                     ]
                                 ], resize_keyboard=True, one_time_keyboard=True))

            await state.set_state('continue_viewing_profiles')

    # Пользователь указал причину жалобы "Продажа товаров и услуг"
    elif option == '🛒 2':
        reason_complaint = 'Продажа товаров и услуг'

        # Получаем количество жалоб на профиль
        complaint = await db.get_user_complaints(current_profile_user_id)

        # Если количество жалоб меньше 3, то прибавляем еще одну жалобу
        if complaint + 1 < 3:
            complaint += 1
            await current_profile.update(complaint=complaint).apply()

            # Добавляем в БД причину жалобы
            await db.add_complaint_for_profile(complaint_profile_id=current_profile_user_id,
                                               reason_complaint=reason_complaint)

        # Если количество жалоб на профиль равно 3, то блокируем профиль
        else:
            complaint += 1
            await current_profile.update(complaint=complaint, enable=False).apply()

            # Добавляем в БД причину жалобы
            await db.add_complaint_for_profile(complaint_profile_id=current_profile_user_id,
                                               reason_complaint=reason_complaint)

        await message.answer(_('Ваша жалоба принята.\n\n'
                               'Жалоба: <b>Продажа товаров и услуг</b>\n\n'
                               'Пользователь: <b>{current_profile.name}, {current_profile.age}</b>').format(
            current_profile))

        # Показываем пользователей, которые написали сообщение
        if current_profile_number + 1 < count_users_send_message:
            # Показываем следующую анкету
            current_profile: models.User = all_users_send_message[current_profile_number + 1]

            photo = current_profile.photo
            game1 = current_profile.game1
            game2 = current_profile.game2

            if game1 is not None and game2 is not None:
                games = f'{game1}, {game2}'
            elif game2 is None:
                games = f'{game1}'
            elif game1 is None:
                games = f'{game2}'
            else:
                games = ''

            # Изменяем текст в зависимости от количества лайков
            if count_users_send_message_for_text == 0:
                text = _('Кому-то понравилась твоя анкета:\n\n'
                         '{current_profile.name}, {current_profile.age} из {current_profile.country}\n'
                         'Хобби: <b>{current_profile.hobby}</b>\n'
                         'О себе: <b>{current_profile.about_yourself}</b>\n'
                         'Играет в игры: <b>{games}</b>'
                         'Письмо: <b>{current_profile.send_message_text}</b>').format(current_profile=current_profile,
                                                                                      games=games)
            else:
                text = _('Кому-то понравилась твоя анкета (и ещё {count_users_send_message_for_text})\n\n'
                         '{current_profile.name}, {current_profile.age} из {current_profile.country}\n'
                         'Хобби: <b>{current_profile.hobby}</b>\n'
                         'О себе: <b>{current_profile.about_yourself}</b>\n'
                         'Играет в игры: <b>{games}</b>'
                         'Письмо: <b>{current_profile.send_message_text}</b>').format(count_users_send_message_for_text,
                                                                                      current_profile=current_profile,
                                                                                      games=games)

            # Если пользователь без фото
            if photo == 'None':
                await message.answer(text=text, reply_markup=get_send_message_keyboard())

            # Если пользователь с фото
            else:
                await message.answer_photo(photo=photo, caption=text,
                                           reply_markup=get_send_message_keyboard())

            await state.update_data(current_profile_send_message_number=current_profile_number + 1,
                                    count_users_send_message_for_text=count_users_send_message_for_text - 1)

            await state.set_state('in_send_message')

        # Сюда попадаем, когда показали всех пользователей, которым понравилась анкета
        else:
            await message.answer(_('Чтобы получать больше лайков ❤️\n'
                                   'Подпишись на канал Ссылка на канал✅'),
                                 reply_markup=ReplyKeyboardMarkup(keyboard=[
                                     [
                                         KeyboardButton(text=_('Продолжить просмотр анкет'))
                                     ]
                                 ], resize_keyboard=True, one_time_keyboard=True))

            await state.set_state('continue_viewing_profiles')

    # Пользователь указал причину жалобы "Не отвечает"
    elif option == '🔇 3':
        reason_complaint = 'Не отвечает'

        # Получаем количество жалоб на профиль
        complaint = await db.get_user_complaints(current_profile_user_id)

        # Если количество жалоб меньше 3, то прибавляем еще одну жалобу
        if complaint + 1 < 3:
            complaint += 1
            await current_profile.update(complaint=complaint).apply()

            # Добавляем в БД причину жалобы
            await db.add_complaint_for_profile(complaint_profile_id=current_profile_user_id,
                                               reason_complaint=reason_complaint)

        # Если количество жалоб на профиль равно 3, то блокируем профиль
        else:
            complaint += 1
            await current_profile.update(complaint=complaint, enable=False).apply()

            # Добавляем в БД причину жалобы
            await db.add_complaint_for_profile(complaint_profile_id=current_profile_user_id,
                                               reason_complaint=reason_complaint)

        await message.answer(_('Ваша жалоба принята.\n\n'
                               'Жалоба: <b>Не отвечает</b>\n\n'
                               'Пользователь: <b>{current_profile.name}, {current_profile.age}</b>').format(
            current_profile=current_profile))

        # Показываем пользователей, которые написали сообщение
        if current_profile_number + 1 < count_users_send_message:

            # Показываем следующую анкету
            current_profile: models.User = all_users_send_message[current_profile_number + 1]

            photo = current_profile.photo
            game1 = current_profile.game1
            game2 = current_profile.game2

            if game1 is not None and game2 is not None:
                games = f'{game1}, {game2}'
            elif game2 is None:
                games = f'{game1}'
            elif game1 is None:
                games = f'{game2}'
            else:
                games = ''

            # Изменяем текст в зависимости от количества лайков
            if count_users_send_message_for_text == 0:
                text = _('Кому-то понравилась твоя анкета:\n\n'
                         '{current_profile.name}, {current_profile.age} из {current_profile.country}\n'
                         'Хобби: <b>{current_profile.hobby}</b>\n'
                         'О себе: <b>{current_profile.about_yourself}</b>\n'
                         'Играет в игры: <b>{games}</b>'
                         'Письмо: <b>{current_profile.send_message_text}</b>').format(
                    current_profile=current_profile, games=games)
            else:
                text = _('Кому-то понравилась твоя анкета (и ещё {count_users_send_message_for_text})\n\n'
                         '{current_profile.name}, {current_profile.age} из {current_profile.country}\n'
                         'Хобби: <b>{current_profile.hobby}</b>\n'
                         'О себе: <b>{current_profile.about_yourself}</b>\n'
                         'Играет в игры: <b>{games}</b>'
                         'Письмо: <b>{current_profile.send_message_text}</b>').format(
                    count_users_send_message_for_text=count_users_send_message_for_text,
                    current_profile=current_profile, games=games)

            # Если пользователь без фото
            if photo == 'None':
                await message.answer(text=text, reply_markup=get_send_message_keyboard())

            # Если пользователь с фото
            else:
                await message.answer_photo(photo=photo, caption=text,
                                           reply_markup=get_send_message_keyboard())

            await state.update_data(current_profile_send_message_number=current_profile_number + 1,
                                    count_users_send_message_for_text=count_users_send_message_for_text - 1)

            await state.set_state('in_send_message')

        # Сюда попадаем, когда показали всех пользователей, которым понравилась анкета
        else:
            await message.answer(_('Чтобы получать больше лайков ❤️\n'
                                   'Подпишись на канал Ссылка на канал✅'),
                                 reply_markup=ReplyKeyboardMarkup(keyboard=[
                                     [
                                         KeyboardButton(text=_('Продолжить просмотр анкет'))
                                     ]
                                 ], resize_keyboard=True, one_time_keyboard=True))

            await state.set_state('continue_viewing_profiles')

    # Пользователь указал причину жалобы "Другое"
    elif option == '❓ 4':
        await message.answer(_('Напишите причину жалобы'))
        await state.set_state('send_message_other_complaint')

    # Пользователь нажал "Отмена"
    elif option == '✖️ 5':
        current_profile: models.User = all_users_send_message[current_profile_number]

        photo = current_profile.photo
        game1 = current_profile.game1
        game2 = current_profile.game2

        if game1 is not None and game2 is not None:
            games = f'{game1}, {game2}'
        elif game2 is None:
            games = f'{game1}'
        elif game1 is None:
            games = f'{game2}'
        else:
            games = ''

        # Изменяем текст в зависимости от количества лайков
        if count_users_send_message_for_text + 1 == 0:
            text = _('Кому-то понравилась твоя анкета:\n\n'
                     '{current_profile.name}, {current_profile.age} из {current_profile.country}\n'
                     'Хобби: <b>{current_profile.hobby}</b>\n'
                     'О себе: <b>{current_profile.about_yourself}</b>\n'
                     'Играет в игры: <b>{games}</b>'
                     'Письмо: <b>{current_profile.send_message_text}</b>').format(current_profile=current_profile,
                                                                                  games=games)
        else:
            text = _('Кому-то понравилась твоя анкета (и ещё {count_users_send_message_for_text + 1})\n\n'
                     '{current_profile.name}, {current_profile.age} из {current_profile.country}\n'
                     'Хобби: <b>{current_profile.hobby}</b>\n'
                     'О себе: <b>{current_profile.about_yourself}</b>\n'
                     'Играет в игры: <b>{games}</b>'
                     'Письмо: <b>{current_profile.send_message_text}</b>').format(current_profile=current_profile,
                                                                                  count_users_send_message_for_text=count_users_send_message_for_text,
                                                                                  games=games)

        # Если пользователь без фото
        if photo == 'None':
            await message.answer(text=text, reply_markup=get_send_message_keyboard())

        # Если пользователь с фото
        else:
            await message.answer_photo(photo=photo, caption=text, reply_markup=get_send_message_keyboard())

        await state.set_state('in_send_message')

    # Пользователь написал сообщение (не нажал ни одну из кнопок)
    else:
        await message.answer(_('Не знаю такой символ'))


# Получаем причину жалобы от пользователя, когда он выбрал вариант "Другое"
@dp.message_handler(state='send_message_other_complaint')
async def get_other_complaint(message: types.Message, state: FSMContext):
    data = await state.get_data()

    # Получаем информацию о пользователе
    second_user: models.User = data.get('second_user')
    language = second_user.language

    # Получаем данные по найденным профилям
    all_users_send_message = data.get('all_users_send_message')
    count_users_send_message = data.get('count_users_send_message')
    count_users_send_message_for_text = data.get('count_users_send_message_for_text') + 1
    current_profile_number = data.get('current_profile_send_message_number')
    current_profile: models.User = all_users_send_message[current_profile_number]
    current_profile_user_id = current_profile[1]
    current_profile: models.User = await db.get_user(current_profile_user_id)

    reason_complaint = message.text

    # Получаем количество жалоб на профиль
    complaint = await db.get_user_complaints(current_profile_user_id)

    # Если количество жалоб меньше 3, то прибавляем еще одну жалобу
    if complaint + 1 < 3:
        complaint += 1
        await current_profile.update(complaint=complaint).apply()

        # Добавляем в БД причину жалобы
        await db.add_complaint_for_profile(complaint_profile_id=current_profile_user_id,
                                           reason_complaint=reason_complaint)

    # Если количество жалоб на профиль равно 3, то блокируем профиль
    else:
        complaint += 1
        await current_profile.update(complaint=complaint, enable=False).apply()

        # Добавляем в БД причину жалобы
        await db.add_complaint_for_profile(complaint_profile_id=current_profile_user_id,
                                           reason_complaint=reason_complaint)

    if language == '🇷🇺 Русский':
        await message.answer(_('Ваша жалоба принята.\n\n'
                               'Жалоба: <b>{reason_complaint}</b>\n\n'
                               'Пользователь: <b>{current_profile.name}, {current_profile.age}</b>').format(
            reason_complaint=reason_complaint, current_profile=current_profile))

    # Показываем пользователей, которые написали сообщение
    if current_profile_number + 1 < count_users_send_message:
        # Показываем следующую анкету
        current_profile: models.User = all_users_send_message[current_profile_number + 1]

        photo = current_profile.photo
        game1 = current_profile.game1
        game2 = current_profile.game2

        if game1 is not None and game2 is not None:
            games = f'{game1}, {game2}'
        elif game2 is None:
            games = f'{game1}'
        elif game1 is None:
            games = f'{game2}'
        else:
            games = ''

        # Изменяем текст в зависимости от количества лайков
        if count_users_send_message_for_text == 0:
            text = _('Кому-то понравилась твоя анкета:\n\n'
                     '{current_profile.name}, {current_profile.age} из {current_profile.country}\n'
                     'Хобби: <b>{current_profile.hobby}</b>\n'
                     'О себе: <b>{current_profile.about_yourself}</b>\n'
                     'Играет в игры: <b>{games}</b>'
                     'Письмо: <b>{current_profile.send_message_text}</b>').format(current_profile=current_profile,
                                                                                  games=games)
        else:
            text = _('Кому-то понравилась твоя анкета (и ещё {count_users_send_message_for_text})\n\n'
                     '{current_profile.name}, {current_profile.age} из {current_profile.country}\n'
                     'Хобби: <b>{current_profile.hobby}</b>\n'
                     'О себе: <b>{current_profile.about_yourself}</b>\n'
                     'Играет в игры: <b>{games}</b>'
                     'Письмо: <b>{current_profile.send_message_text}</b>').format(
                count_users_send_message_for_text=count_users_send_message_for_text, current_profile=current_profile,
                games=games)

        # Если пользователь без фото
        if photo == 'None':
            await message.answer(text=text, reply_markup=get_send_message_keyboard())

        # Если пользователь с фото
        else:
            await message.answer_photo(photo=photo, caption=text,
                                       reply_markup=get_send_message_keyboard())

        await state.update_data(current_profile_send_message_number=current_profile_number + 1,
                                count_users_send_message_for_text=count_users_send_message_for_text - 1)

        await state.set_state('in_send_message')

    # Сюда попадаем, когда показали всех пользователей, которым понравилась анкета
    else:
        await message.answer(_('Чтобы получать больше лайков ❤️\n'
                               'Подпишись на канал Ссылка на канал✅'),
                             reply_markup=ReplyKeyboardMarkup(keyboard=[
                                 [
                                     KeyboardButton(text=_('Продолжить просмотр анкет'))
                                 ]
                             ], resize_keyboard=True, one_time_keyboard=True))

        await state.set_state('continue_viewing_profiles')


# Сюда попадаем, когда пользователь 2 написал сообщение пользователю 1
@dp.message_handler(state='in_send_message_wait_answer')
async def send_answer_message(message: types.Message, state: FSMContext):
    data = await state.get_data()

    # Получаем информацию о пользователе
    second_user: models.User = data.get('second_user')
    user_language = second_user.language
    second_user_link_username = f'<a href="https://t.me/{second_user.username}">{second_user.name}</a>'
    answer_text = message.text

    # Получаем данные по найденным профилям
    all_users_send_message = data.get('all_users_send_message')
    count_users_send_message = data.get('count_users_send_message')
    current_profile_number = data.get('current_profile_send_message_number')
    count_users_send_message_for_text = (count_users_send_message - 1) - current_profile_number
    current_profile_send_msg: models.User = all_users_send_message[current_profile_number]
    current_profile_user_id = current_profile_send_msg[1]
    current_profile: models.User = await db.get_user(current_profile_user_id)
    # user_send_message_link = f'<a href="tg://user?id={current_profile.user_id}">{current_profile.name}</a>'
    user_send_message_link_username = f'<a href="https://t.me/{current_profile.username}">{current_profile.name}</a>'
    language_current_profile = current_profile.language

    # Отправляем информацию о взаимной симпатии пользователю 2
    await message.answer(_('Есть взаимная симпатия! Начинай общаться 👉 {user_send_message_link_username}').format(
        user_send_message_link_username=user_send_message_link_username),
        disable_web_page_preview=True)

    # Устанавливаем у прочитанного сообщение признак "Прочитано"
    await db.setting_the_attribute_read(current_profile_send_msg[0])

    # Отправляем информацию о взаимной симпатии пользователю 1
    await bot.send_message(chat_id=f'{current_profile.user_id}', text=answer_text)
    await bot.send_message(chat_id=f'{current_profile.user_id}',
                           text=_('Есть взаимная симпатия! Начинай общаться 👉 {second_user_link_username}').format(
                               second_user_link_username=second_user_link_username),
                           disable_web_page_preview=True)

    # Показываем пользователей, которые написали сообщение
    if current_profile_number + 1 < count_users_send_message:

        if count_users_send_message_for_text == 1:
            caption = _('Твоя анкета понравилась {count_users_send_message_for_text} пользователю, '
                        'показать его?\n\n'
                        '1. Показать.\n'
                        '2. Не хочу больше никого смотреть.').format(count_users_send_message_for_text)
        elif count_users_send_message_for_text % 10 == 1:
            caption = _('Твоя анкета понравилась {count_users_send_message_for_text} пользователю, '
                        'показать их?\n\n'
                        '1. Показать.\n'
                        '2. Не хочу больше никого смотреть.').format(count_users_send_message_for_text)
        else:
            caption = _('Твоя анкета понравилась {count_users_send_message_for_text} пользователям, '
                        'показать их?\n\n'
                        '1. Показать.\n'
                        '2. Не хочу больше никого смотреть.').format(count_users_send_message_for_text)

        await message.answer(text=caption, reply_markup=profile_action_like_keyboard)

        await state.set_state('in_send_message')

    # Сюда попадаем, когда показали всех пользователей, которым понравилась анкета
    else:
        await message.answer(_('Чтобы получать больше лайков ❤️\n'
                               'Подпишись на канал Ссылка на канал✅'),
                             reply_markup=ReplyKeyboardMarkup(keyboard=[
                                 [
                                     KeyboardButton(text=_('Продолжить просмотр анкет'))
                                 ]
                             ], resize_keyboard=True, one_time_keyboard=True))

        await state.set_state('continue_viewing_profiles')


# Сюда попадаем, когда пользователь нажал "Продолжить просмотр анкет"
@dp.message_handler(state='continue_viewing_profiles')
async def viewing_profiles(message: types.Message, state: FSMContext):
    data = await state.get_data()

    # Получаем информацию о пользователе
    second_user: models.User = data.get('second_user')
    user_language = second_user.language
    purpose = second_user.purpose

    msg = await message.answer(_('Ищу подходящие анкеты 🔍'))
    async for __ in await async_range(4):
        msg = await bot.edit_message_text(text=_('Ищу подходящие анкеты 🔎'),
                                          chat_id=message.from_user.id,
                                          message_id=msg.message_id)

        await asyncio.sleep(.5)

        msg = await bot.edit_message_text(text=_('Ищу подходящие анкеты 🔍'),
                                          chat_id=message.from_user.id,
                                          message_id=msg.message_id)

    find_users = await find_query.find_user_to_purpose(message.from_user.id)
    count_profiles = len(find_users)

    try:
        first_profile: models.User = find_users[0]

        await state.update_data(profiles=find_users, count_profiles=count_profiles)

        game1 = first_profile.game1
        game2 = first_profile.game2

        if game1 is not None and game2 is not None:
            games = f'{game1}, {game2}'
        elif game2 is None:
            games = f'{game1}'
        elif game1 is None:
            games = f'{game2}'
        else:
            games = ''

        if count_profiles % 10 == 1:
            await message.answer(_('По вашему запросу найден {count_profiles} профиль').format(count_profiles))
        elif 1 < count_profiles % 10 < 5:
            await message.answer(_('По вашему запросу найдено {count_profiles} профиля').format(count_profiles))
        else:
            await message.answer(_('По вашему запросу найдено {count_profiles} профилей').format(count_profiles))

        # Если пользователь ищет анкеты, чтобы просто поиграть
        if purpose in ['Просто поиграть', 'Just to play']:
            text_just_play = _('Возраст: <b>{first_profile.age}</b>\n'
                               'Пол: <b>{first_profile.gender}</b>\n'
                               'Цель: <b>{first_profile.purpose}</b>\n'
                               'Уровень игры: <b>{first_profile.play_level}</b>\n'
                               'К/Д: <b>{first_profile.cool_down}</b>\n'
                               'О себе: <b>{first_profile.about_yourself}</b>\n'
                               'Играет в игры: <b>{games}</b>').format(first_profile=first_profile, games=games)

            if first_profile.photo == 'None':
                await message.answer(text=text_just_play,
                                     reply_markup=action_for_profile(profiles=find_users,
                                                                     count_profiles=count_profiles,
                                                                     current_profile=0))
            else:
                await message.answer_photo(first_profile.photo,
                                           caption=text_just_play,
                                           reply_markup=action_for_profile(profiles=find_users,
                                                                           count_profiles=count_profiles,
                                                                           current_profile=0))

            await state.set_state('find_profiles_just_play')

        # Если пользователь ищет анкеты, чтобы познакомиться
        elif purpose in ['Человека в реальной жизни', 'A person in real life']:
            text_real_life = _('{first_profile.name}, {first_profile.age} из {first_profile.country}\n'
                               'Хобби: <b>{first_profile.hobby}</b>\n'
                               'О себе: <b>{first_profile.about_yourself}</b>\n'
                               'Играет в игры: <b>{games}</b>').format(first_profile=first_profile, games=games)

            if first_profile.photo == 'None':
                await message.answer(text=text_real_life,
                                     reply_markup=action_for_profile(profiles=find_users,
                                                                     count_profiles=count_profiles,
                                                                     current_profile=0))
            else:
                await message.answer_photo(first_profile.photo,
                                           caption=text_real_life,
                                           reply_markup=action_for_profile(profiles=find_users,
                                                                           count_profiles=count_profiles,
                                                                           current_profile=0))

            await state.set_state('find_profiles')

        await state.update_data(language=user_language,
                                profiles=find_users,
                                count_profiles=count_profiles,
                                current_profile_number=0)

    except IndexError:
        await message.answer(_('По вашим критериям поиска не нашлось анкет.\n\n'
                               'Попробуйте поискать позднее или измените критерии поиска.'))
