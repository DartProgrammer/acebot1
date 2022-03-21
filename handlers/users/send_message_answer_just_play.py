import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from emoji.core import emojize

from handlers.users.my_profile import find_query
from keyboards.inline.gaming_keyboards import get_send_message_keyboard, \
    complain_keyboard, profile_action_like_keyboard, action_for_profile
from loader import dp, bot, db
from utils.db_api import models


# Здесь ловим действия со стороны пользователя 2, когда пользователь 1 написал письмо

# Если пользователь нажал 👍 (Показать)
@dp.message_handler(text='👍', state='in_send_message_just_play')
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

    if language_second_user == '🇷🇺 Русский':
        # Изменяем текст в зависимости от количества лайков
        if count_users_send_message == 1:
            text = f'Кому-то понравилась твоя анкета:\n\n' \
                   f'Возраст: {current_profile.age}\n' \
                   f'Пол: {current_profile.gender}\n' \
                   f'О себе: {current_profile.about_yourself}\n' \
                   f'Играет в: {games}\n' \
                   f'Уровень игры: {current_profile.play_level}\n' \
                   f'К/Д: {current_profile.cool_down}\n\n' \
                   f'Письмо: <b>{current_profile.send_message_text}</b>'
        else:
            text = f'Кому-то понравилась твоя анкета (и ещё {count_users_send_message_for_text})\n\n' \
                   f'Возраст: {current_profile.age}\n' \
                   f'Пол: {current_profile.gender}\n' \
                   f'О себе: {current_profile.about_yourself}\n' \
                   f'Играет в: {games}\n' \
                   f'Уровень игры: {current_profile.play_level}\n' \
                   f'К/Д: {current_profile.cool_down}\n\n' \
                   f'Письмо: <b>{current_profile.send_message_text}</b>'

    else:
        if count_users_send_message == 1:
            text = f'Someone liked your profile:\n\n' \
                   f'Age: {current_profile.age}\n' \
                   f'Gender: {current_profile.gender}\n' \
                   f'About: {current_profile.about_yourself}\n' \
                   f'Играет в: {games}\n' \
                   f'Level of play: {current_profile.play_level}\n' \
                   f'Cool down: {current_profile.cool_down}\n\n' \
                   f'Message: <b>{current_profile.send_message_text}</b>'
        else:
            text = f'Someone liked your profile (and more {count_users_send_message_for_text})\n\n' \
                   f'Age: {current_profile.age}\n' \
                   f'Gender: {current_profile.gender}\n' \
                   f'About: {current_profile.about_yourself}\n' \
                   f'Играет в: {games}\n' \
                   f'Level of play: {current_profile.play_level}\n' \
                   f'Cool down: {current_profile.cool_down}\n\n' \
                   f'Message: <b>{current_profile.send_message_text}</b>'

    # Если пользователь без фото
    if photo == 'None':
        await message.answer(text=text, reply_markup=get_send_message_keyboard(language_second_user))

    # Если пользователь с фото
    else:
        await message.answer_photo(photo=photo, caption=text,
                                   reply_markup=get_send_message_keyboard(language_second_user))


# Если пользователь нажал 💤 (Не хочу больше никого смотреть)
@dp.message_handler(text='💤', state='in_send_message_just_play')
async def not_show_users_profiles(message: types.Message, state: FSMContext):
    second_user_id = message.from_user.id
    second_user: models.User = await db.get_user(second_user_id)
    language = second_user.language
    await state.update_data(second_user=second_user)

    if language == '🇷🇺 Русский':
        text = 'Так ты не узнаешь, что кому-то нравишься... ' \
               'Точно хочешь отключить свою анкету?\n\n' \
               '1. Да, отключить анкету.\n' \
               '2. Нет, вернуться назад.'
    else:
        text = "That way you won't know that someone likes you... " \
               "Are you sure you want to disable your profile?\n\n" \
               "1. Yes, disable the profile.\n" \
               "2. No, go back."

    await message.answer(text=text, reply_markup=ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(text='1'),
            KeyboardButton(text='2')
        ]
    ], resize_keyboard=True, one_time_keyboard=True))

    await state.set_state('disable_second_profile_send_message_just_play')


# Сюда попадаем, когда пользователь нажал "Ответить" или "⚠️ Пожаловаться"
@dp.message_handler(state='in_send_message_just_play')
async def answer_message(message: types.Message, state: FSMContext):
    data = await state.get_data()

    # Получаем информацию о пользователе
    second_user: models.User = data.get('second_user')
    user_language = second_user.language

    if message.text in ['Ответить', 'Answer']:
        if user_language == '🇷🇺 Русский':
            await message.answer('Напишите сообщение, которое хотите отправить')
        else:
            await message.answer('Write the message you want to send')

        await state.set_state('in_send_message_just_play_wait_answer')

    elif message.text in ['⚠️ Пожаловаться', '⚠️ Complain']:
        if user_language == '🇷🇺 Русский':
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

        await state.set_state('send_message_just_play_reason_complaint')


# Сюда попадаем, когда пользователь выбрал причину жалобы
@dp.message_handler(state='send_message_just_play_reason_complaint')
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

        if language == '🇷🇺 Русский':
            await message.answer(f'Ваша жалоба принята.\n\n'
                                 f'Жалоба: <b>Материал для взрослых</b>\n\n'
                                 f'Пользователь: <b>{current_profile.name}, {current_profile.age}</b>')
        else:
            await message.answer(f'Your complaint has been accepted.\n\n'
                                 f'Complaint: <b>Adult material</b>\n\n'
                                 f'User: <b>{current_profile.name}, {current_profile.age}</b>')

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

            if language == '🇷🇺 Русский':
                # Изменяем текст в зависимости от количества лайков
                if count_users_send_message_for_text == 0:
                    text = f'Кому-то понравилась твоя анкета:\n\n' \
                           f'Возраст: {current_profile.age}\n' \
                           f'Пол: {current_profile.gender}\n' \
                           f'О себе: {current_profile.about_yourself}\n' \
                           f'Играет в: {games}\n' \
                           f'Уровень игры: {current_profile.play_level}\n' \
                           f'К/Д: {current_profile.cool_down}\n\n' \
                           f'Письмо: <b>{current_profile.send_message_text}</b>'
                else:
                    text = f'Кому-то понравилась твоя анкета (и ещё {count_users_send_message_for_text})\n\n' \
                           f'Возраст: {current_profile.age}\n' \
                           f'Пол: {current_profile.gender}\n' \
                           f'О себе: {current_profile.about_yourself}\n' \
                           f'Играет в: {games}\n' \
                           f'Уровень игры: {current_profile.play_level}\n' \
                           f'К/Д: {current_profile.cool_down}\n\n' \
                           f'Письмо: <b>{current_profile.send_message_text}</b>'

            else:
                if count_users_send_message_for_text == 0:
                    text = f'Someone liked your profile:\n\n' \
                           f'Age: {current_profile.age}\n' \
                           f'Gender: {current_profile.gender}\n' \
                           f'About: {current_profile.about_yourself}\n' \
                           f'Играет в: {games}\n' \
                           f'Level of play: {current_profile.play_level}\n' \
                           f'Cool down: {current_profile.cool_down}\n\n' \
                           f'Message: <b>{current_profile.send_message_text}</b>'
                else:
                    text = f'Someone liked your profile (and more {count_users_send_message_for_text})\n\n' \
                           f'Age: {current_profile.age}\n' \
                           f'Gender: {current_profile.gender}\n' \
                           f'About: {current_profile.about_yourself}\n' \
                           f'Играет в: {games}\n' \
                           f'Level of play: {current_profile.play_level}\n' \
                           f'Cool down: {current_profile.cool_down}\n\n' \
                           f'Message: <b>{current_profile.send_message_text}</b>'

            # Если пользователь без фото
            if photo == 'None':
                await message.answer(text=text, reply_markup=get_send_message_keyboard(language))

            # Если пользователь с фото
            else:
                await message.answer_photo(photo=photo, caption=text,
                                           reply_markup=get_send_message_keyboard(language))

            await state.update_data(current_profile_send_message_number=current_profile_number + 1,
                                    count_users_send_message_for_text=count_users_send_message_for_text - 1)

            await state.set_state('in_send_message_just_play')

        # Сюда попадаем, когда показали всех пользователей, которым понравилась анкета
        else:
            if language == '🇷🇺 Русский':
                await message.answer(f'Чтобы получать больше лайков ❤️\n'
                                     f'Подпишись на канал Ссылка на канал✅',
                                     reply_markup=ReplyKeyboardMarkup(keyboard=[
                                         [
                                             KeyboardButton(text='Продолжить просмотр анкет')
                                         ]
                                     ], resize_keyboard=True, one_time_keyboard=True))
            else:
                await message.answer(f'To get more likes ❤️\n'
                                     f'Subscribe to the channel Link ✅',
                                     reply_markup=ReplyKeyboardMarkup(keyboard=[
                                         [
                                             KeyboardButton(text='Continue viewing profiles')
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

        if language == '🇷🇺 Русский':
            await message.answer(f'Ваша жалоба принята.\n\n'
                                 f'Жалоба: <b>Продажа товаров и услуг</b>\n\n'
                                 f'Пользователь: <b>{current_profile.name}, {current_profile.age}</b>')
        else:
            await message.answer(f'Your complaint has been accepted.\n\n'
                                 f'Complaint: <b>Sale of goods and services</b>\n\n'
                                 f'User: <b>{current_profile.name}, {current_profile.age}</b>')

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

            if language == '🇷🇺 Русский':
                # Изменяем текст в зависимости от количества лайков
                if count_users_send_message_for_text == 0:
                    text = f'Кому-то понравилась твоя анкета:\n\n' \
                           f'Возраст: {current_profile.age}\n' \
                           f'Пол: {current_profile.gender}\n' \
                           f'О себе: {current_profile.about_yourself}\n' \
                           f'Играет в: {games}\n' \
                           f'Уровень игры: {current_profile.play_level}\n' \
                           f'К/Д: {current_profile.cool_down}\n\n' \
                           f'Письмо: <b>{current_profile.send_message_text}</b>'
                else:
                    text = f'Кому-то понравилась твоя анкета (и ещё {count_users_send_message_for_text})\n\n' \
                           f'Возраст: {current_profile.age}\n' \
                           f'Пол: {current_profile.gender}\n' \
                           f'О себе: {current_profile.about_yourself}\n' \
                           f'Играет в: {games}\n' \
                           f'Уровень игры: {current_profile.play_level}\n' \
                           f'К/Д: {current_profile.cool_down}\n\n' \
                           f'Письмо: <b>{current_profile.send_message_text}</b>'

            else:
                if count_users_send_message_for_text == 0:
                    text = f'Someone liked your profile:\n\n' \
                           f'Age: {current_profile.age}\n' \
                           f'Gender: {current_profile.gender}\n' \
                           f'About: {current_profile.about_yourself}\n' \
                           f'Играет в: {games}\n' \
                           f'Level of play: {current_profile.play_level}\n' \
                           f'Cool down: {current_profile.cool_down}\n\n' \
                           f'Message: <b>{current_profile.send_message_text}</b>'
                else:
                    text = f'Someone liked your profile (and more {count_users_send_message_for_text})\n\n' \
                           f'Age: {current_profile.age}\n' \
                           f'Gender: {current_profile.gender}\n' \
                           f'About: {current_profile.about_yourself}\n' \
                           f'Играет в: {games}\n' \
                           f'Level of play: {current_profile.play_level}\n' \
                           f'Cool down: {current_profile.cool_down}\n\n' \
                           f'Message: <b>{current_profile.send_message_text}</b>'

            # Если пользователь без фото
            if photo == 'None':
                await message.answer(text=text, reply_markup=get_send_message_keyboard(language))

            # Если пользователь с фото
            else:
                await message.answer_photo(photo=photo, caption=text,
                                           reply_markup=get_send_message_keyboard(language))

            await state.update_data(current_profile_send_message_number=current_profile_number + 1,
                                    count_users_send_message_for_text=count_users_send_message_for_text - 1)

            await state.set_state('in_send_message_just_play')

        # Сюда попадаем, когда показали всех пользователей, которым понравилась анкета
        else:
            if language == '🇷🇺 Русский':
                await message.answer(f'Чтобы получать больше лайков ❤️\n'
                                     f'Подпишись на канал Ссылка на канал✅',
                                     reply_markup=ReplyKeyboardMarkup(keyboard=[
                                         [
                                             KeyboardButton(text='Продолжить просмотр анкет')
                                         ]
                                     ], resize_keyboard=True, one_time_keyboard=True))
            else:
                await message.answer(f'To get more likes ❤️\n'
                                     f'Subscribe to the channel Link ✅',
                                     reply_markup=ReplyKeyboardMarkup(keyboard=[
                                         [
                                             KeyboardButton(text='Continue viewing profiles')
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

        if language == '🇷🇺 Русский':
            await message.answer(f'Ваша жалоба принята.\n\n'
                                 f'Жалоба: <b>Не отвечает</b>\n\n'
                                 f'Пользователь: <b>{current_profile.name}, {current_profile.age}</b>')
        else:
            await message.answer(f'Your complaint has been accepted.\n\n'
                                 f'Complaint: <b>Not responding</b>\n\n'
                                 f'User: <b>{current_profile.name}, {current_profile.age}</b>')

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

            if language == '🇷🇺 Русский':
                # Изменяем текст в зависимости от количества лайков
                if count_users_send_message_for_text == 0:
                    text = f'Кому-то понравилась твоя анкета:\n\n' \
                           f'Возраст: {current_profile.age}\n' \
                           f'Пол: {current_profile.gender}\n' \
                           f'О себе: {current_profile.about_yourself}\n' \
                           f'Играет в: {games}\n' \
                           f'Уровень игры: {current_profile.play_level}\n' \
                           f'К/Д: {current_profile.cool_down}\n\n' \
                           f'Письмо: <b>{current_profile.send_message_text}</b>'
                else:
                    text = f'Кому-то понравилась твоя анкета (и ещё {count_users_send_message_for_text})\n\n' \
                           f'Возраст: {current_profile.age}\n' \
                           f'Пол: {current_profile.gender}\n' \
                           f'О себе: {current_profile.about_yourself}\n' \
                           f'Играет в: {games}\n' \
                           f'Уровень игры: {current_profile.play_level}\n' \
                           f'К/Д: {current_profile.cool_down}\n\n' \
                           f'Письмо: <b>{current_profile.send_message_text}</b>'

            else:
                if count_users_send_message_for_text == 0:
                    text = f'Someone liked your profile:\n\n' \
                           f'Age: {current_profile.age}\n' \
                           f'Gender: {current_profile.gender}\n' \
                           f'About: {current_profile.about_yourself}\n' \
                           f'Играет в: {games}\n' \
                           f'Level of play: {current_profile.play_level}\n' \
                           f'Cool down: {current_profile.cool_down}\n\n' \
                           f'Message: <b>{current_profile.send_message_text}</b>'
                else:
                    text = f'Someone liked your profile (and more {count_users_send_message_for_text})\n\n' \
                           f'Age: {current_profile.age}\n' \
                           f'Gender: {current_profile.gender}\n' \
                           f'About: {current_profile.about_yourself}\n' \
                           f'Играет в: {games}\n' \
                           f'Level of play: {current_profile.play_level}\n' \
                           f'Cool down: {current_profile.cool_down}\n\n' \
                           f'Message: <b>{current_profile.send_message_text}</b>'

            # Если пользователь без фото
            if photo == 'None':
                await message.answer(text=text, reply_markup=get_send_message_keyboard(language))

            # Если пользователь с фото
            else:
                await message.answer_photo(photo=photo, caption=text,
                                           reply_markup=get_send_message_keyboard(language))

            await state.update_data(current_profile_send_message_number=current_profile_number + 1,
                                    count_users_send_message_for_text=count_users_send_message_for_text - 1)

            await state.set_state('in_send_message_just_play')

        # Сюда попадаем, когда показали всех пользователей, которым понравилась анкета
        else:
            if language == '🇷🇺 Русский':
                await message.answer(f'Чтобы получать больше лайков ❤️\n'
                                     f'Подпишись на канал Ссылка на канал✅',
                                     reply_markup=ReplyKeyboardMarkup(keyboard=[
                                         [
                                             KeyboardButton(text='Продолжить просмотр анкет')
                                         ]
                                     ], resize_keyboard=True, one_time_keyboard=True))
            else:
                await message.answer(f'To get more likes ❤️\n'
                                     f'Subscribe to the channel Link ✅',
                                     reply_markup=ReplyKeyboardMarkup(keyboard=[
                                         [
                                             KeyboardButton(text='Continue viewing profiles')
                                         ]
                                     ], resize_keyboard=True, one_time_keyboard=True))

            await state.set_state('continue_viewing_profiles')

    # Пользователь указал причину жалобы "Другое"
    elif option == '❓ 4':

        if language == '🇷🇺 Русский':
            await message.answer('Напишите причину жалобы')
        else:
            await message.answer('Write the reason for the complaint')

        await state.set_state('send_message_just_play_other_complaint')

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

        if language == '🇷🇺 Русский':
            # Изменяем текст в зависимости от количества лайков
            if count_users_send_message_for_text + 1 == 0:
                text = f'Кому-то понравилась твоя анкета:\n\n' \
                       f'Возраст: {current_profile.age}\n' \
                       f'Пол: {current_profile.gender}\n' \
                       f'О себе: {current_profile.about_yourself}\n' \
                       f'Играет в: {games}\n' \
                       f'Уровень игры: {current_profile.play_level}\n' \
                       f'К/Д: {current_profile.cool_down}\n\n' \
                       f'Письмо: <b>{current_profile.send_message_text}</b>'
            else:
                text = f'Кому-то понравилась твоя анкета (и ещё {count_users_send_message_for_text + 1})\n\n' \
                       f'Возраст: {current_profile.age}\n' \
                       f'Пол: {current_profile.gender}\n' \
                       f'О себе: {current_profile.about_yourself}\n' \
                       f'Играет в: {games}\n' \
                       f'Уровень игры: {current_profile.play_level}\n' \
                       f'К/Д: {current_profile.cool_down}\n\n' \
                       f'Письмо: <b>{current_profile.send_message_text}</b>'

        else:
            if count_users_send_message_for_text + 1 == 0:
                text = f'Someone liked your profile:\n\n' \
                       f'Age: {current_profile.age}\n' \
                       f'Gender: {current_profile.gender}\n' \
                       f'About: {current_profile.about_yourself}\n' \
                       f'Играет в: {games}\n' \
                       f'Level of play: {current_profile.play_level}\n' \
                       f'Cool down: {current_profile.cool_down}\n\n' \
                       f'Message: <b>{current_profile.send_message_text}</b>'
            else:
                text = f'Someone liked your profile (and more {count_users_send_message_for_text + 1})\n\n' \
                       f'Age: {current_profile.age}\n' \
                       f'Gender: {current_profile.gender}\n' \
                       f'About: {current_profile.about_yourself}\n' \
                       f'Играет в: {games}\n' \
                       f'Level of play: {current_profile.play_level}\n' \
                       f'Cool down: {current_profile.cool_down}\n\n' \
                       f'Message: <b>{current_profile.send_message_text}</b>'

        # Если пользователь без фото
        if photo == 'None':
            await message.answer(text=text, reply_markup=get_send_message_keyboard(language))

        # Если пользователь с фото
        else:
            await message.answer_photo(photo=photo, caption=text, reply_markup=get_send_message_keyboard(language))

        await state.set_state('in_send_message_just_play')

    # Пользователь написал сообщение (не нажал ни одну из кнопок)
    else:
        if language == '🇷🇺 Русский':
            await message.answer('Не знаю такой символ')
        else:
            await message.answer("I don't know such a symbol")


# Получаем причину жалобы от пользователя, когда он выбрал вариант "Другое"
@dp.message_handler(state='send_message_just_play_other_complaint')
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
        await message.answer(f'Ваша жалоба принята.\n\n'
                             f'Жалоба: <b>{reason_complaint}</b>\n\n'
                             f'Пользователь: <b>{current_profile.name}, {current_profile.age}</b>')
    else:
        await message.answer(f'Your complaint has been accepted.\n\n'
                             f'Complaint: <b>{reason_complaint}</b>\n\n'
                             f'User: <b>{current_profile.name}, {current_profile.age}</b>')

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

        if language == '🇷🇺 Русский':
            # Изменяем текст в зависимости от количества лайков
            if count_users_send_message_for_text == 0:
                text = f'Кому-то понравилась твоя анкета:\n\n' \
                       f'Возраст: {current_profile.age}\n' \
                       f'Пол: {current_profile.gender}\n' \
                       f'О себе: {current_profile.about_yourself}\n' \
                       f'Играет в: {games}\n' \
                       f'Уровень игры: {current_profile.play_level}\n' \
                       f'К/Д: {current_profile.cool_down}\n\n' \
                       f'Письмо: <b>{current_profile.send_message_text}</b>'
            else:
                text = f'Кому-то понравилась твоя анкета (и ещё {count_users_send_message_for_text})\n\n' \
                       f'Возраст: {current_profile.age}\n' \
                       f'Пол: {current_profile.gender}\n' \
                       f'О себе: {current_profile.about_yourself}\n' \
                       f'Играет в: {games}\n' \
                       f'Уровень игры: {current_profile.play_level}\n' \
                       f'К/Д: {current_profile.cool_down}\n\n' \
                       f'Письмо: <b>{current_profile.send_message_text}</b>'

        else:
            if count_users_send_message_for_text == 0:
                text = f'Someone liked your profile:\n\n' \
                       f'Age: {current_profile.age}\n' \
                       f'Gender: {current_profile.gender}\n' \
                       f'About: {current_profile.about_yourself}\n' \
                       f'Играет в: {games}\n' \
                       f'Level of play: {current_profile.play_level}\n' \
                       f'Cool down: {current_profile.cool_down}\n\n' \
                       f'Message: <b>{current_profile.send_message_text}</b>'
            else:
                text = f'Someone liked your profile (and more {count_users_send_message_for_text})\n\n' \
                       f'Age: {current_profile.age}\n' \
                       f'Gender: {current_profile.gender}\n' \
                       f'About: {current_profile.about_yourself}\n' \
                       f'Играет в: {games}\n' \
                       f'Level of play: {current_profile.play_level}\n' \
                       f'Cool down: {current_profile.cool_down}\n\n' \
                       f'Message: <b>{current_profile.send_message_text}</b>'

        # Если пользователь без фото
        if photo == 'None':
            await message.answer(text=text, reply_markup=get_send_message_keyboard(language))

        # Если пользователь с фото
        else:
            await message.answer_photo(photo=photo, caption=text,
                                       reply_markup=get_send_message_keyboard(language))

        await state.update_data(current_profile_send_message_number=current_profile_number + 1,
                                count_users_send_message_for_text=count_users_send_message_for_text - 1)

        await state.set_state('in_send_message_just_play')

    # Сюда попадаем, когда показали всех пользователей, которым понравилась анкета
    else:
        if language == '🇷🇺 Русский':
            await message.answer(f'Чтобы получать больше лайков ❤️\n'
                                 f'Подпишись на канал Ссылка на канал✅',
                                 reply_markup=ReplyKeyboardMarkup(keyboard=[
                                     [
                                         KeyboardButton(text='Продолжить просмотр анкет')
                                     ]
                                 ], resize_keyboard=True, one_time_keyboard=True))
        else:
            await message.answer(f'To get more likes ❤️\n'
                                 f'Subscribe to the channel Link ✅',
                                 reply_markup=ReplyKeyboardMarkup(keyboard=[
                                     [
                                         KeyboardButton(text='Continue viewing profiles')
                                     ]
                                 ], resize_keyboard=True, one_time_keyboard=True))

        await state.set_state('continue_viewing_profiles')


# Сюда попадаем, когда пользователь 2 написал сообщение пользователю 1
@dp.message_handler(state='in_send_message_just_play_wait_answer')
async def send_answer_message(message: types.Message, state: FSMContext):
    data = await state.get_data()

    # Получаем информацию о пользователе
    second_user: models.User = data.get('second_user')
    user_language = second_user.language
    # second_user_link = f'<a href="tg://user?id={second_user.user_id}">{second_user.name}</a>'
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
    if user_language == '🇷🇺 Русский':
        await message.answer(f'Есть взаимная симпатия! Начинай общаться 👉 {user_send_message_link_username}',
                             disable_web_page_preview=True)
    else:
        await message.answer(f'There is mutual sympathy! Start chatting 👉 {user_send_message_link_username}',
                             disable_web_page_preview=True)

    # Устанавливаем у прочитанного сообщение признак "Прочитано"
    await db.setting_the_attribute_read(current_profile_send_msg[0])

    # Отправляем информацию о взаимной симпатии пользователю 1
    if language_current_profile == '🇷🇺 Русский':
        await bot.send_message(chat_id=f'{current_profile.user_id}', text=answer_text)
        await bot.send_message(chat_id=f'{current_profile.user_id}',
                               text=f'Есть взаимная симпатия! Начинай общаться 👉 {second_user_link_username}',
                               disable_web_page_preview=True)
    else:
        await bot.send_message(chat_id=f'{current_profile.user_id}', text=answer_text)
        await bot.send_message(chat_id=f'{current_profile.user_id}',
                               text=f'There is mutual sympathy! Start chatting 👉 {second_user_link_username}',
                               disable_web_page_preview=True)

    # Показываем пользователей, которые написали сообщение
    if current_profile_number + 1 < count_users_send_message:

        # Если текущий язык анкеты пользователя Русский
        if user_language == '🇷🇺 Русский':
            if count_users_send_message_for_text == 1:
                caption = f'Твоя анкета понравилась {count_users_send_message_for_text} пользователю, ' \
                          f'показать его?\n\n' \
                          f'1. Показать.\n' \
                          f'2. Не хочу больше никого смотреть.'
            elif count_users_send_message_for_text % 10 == 1:
                caption = f'Твоя анкета понравилась {count_users_send_message_for_text} пользователю, ' \
                          f'показать их?\n\n' \
                          f'1. Показать.\n' \
                          f'2. Не хочу больше никого смотреть.'
            else:
                caption = f'Твоя анкета понравилась {count_users_send_message_for_text} пользователям, ' \
                          f'показать их?\n\n' \
                          f'1. Показать.\n' \
                          f'2. Не хочу больше никого смотреть.'

        # Если текущий язык анкеты пользователя Английский
        else:
            if count_users_send_message == 1:
                caption = f'{count_users_send_message} user liked your profile, should I show it?\n\n' \
                          f'1. Show.\n' \
                          f"2. I don't want to watch anyone."
            elif count_users_send_message % 10 == 1:
                caption = f'{count_users_send_message} users liked your profile, should I show them?\n\n' \
                          f'1. Show.\n' \
                          f"2. I don't want to watch anyone."
            else:
                caption = f'{count_users_send_message} users liked your profile, should I show them?\n\n' \
                          f'1. Show.\n' \
                          f"2. I don't want to watch anyone."

        await message.answer(text=caption, reply_markup=profile_action_like_keyboard)

        await state.set_state('in_send_message_just_play')

    # Сюда попадаем, когда показали всех пользователей, которым понравилась анкета
    else:
        if user_language == '🇷🇺 Русский':
            await message.answer(f'Чтобы получать больше лайков ❤️\n'
                                 f'Подпишись на канал Ссылка на канал✅',
                                 reply_markup=ReplyKeyboardMarkup(keyboard=[
                                     [
                                         KeyboardButton(text='Продолжить просмотр анкет')
                                     ]
                                 ], resize_keyboard=True, one_time_keyboard=True))
        else:
            await message.answer(f'To get more likes ❤️\n'
                                 f'Subscribe to the channel Link ✅',
                                 reply_markup=ReplyKeyboardMarkup(keyboard=[
                                     [
                                         KeyboardButton(text='Continue viewing profiles')
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

    if user_language == '🇷🇺 Русский':
        search_text = 'Ищу подходящие анкеты'
    else:
        search_text = 'Looking for suitable profiles'

    msg = await message.answer(f'{search_text} 🔍')
    symbol1 = '🔎'
    symbol2 = '🔍'
    i = 0
    while i != 5:
        msg = await bot.edit_message_text(text=f'{search_text} {symbol1}',
                                          chat_id=message.from_user.id,
                                          message_id=msg.message_id)

        await asyncio.sleep(.5)

        msg = await bot.edit_message_text(text=f'{search_text} {symbol2}',
                                          chat_id=message.from_user.id,
                                          message_id=msg.message_id)
        i += 1

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

        if user_language == '🇷🇺 Русский':
            if count_profiles % 10 == 1:
                await message.answer(f'По вашему запросу найден {count_profiles} профиль')
            elif 1 < count_profiles % 10 < 5:
                await message.answer(f'По вашему запросу найдено {count_profiles} профиля')
            else:
                await message.answer(f'По вашему запросу найдено {count_profiles} профилей')
        else:
            if count_profiles % 10 == 1:
                await message.answer(f'For your query was found {count_profiles} profile(s)')
            elif 1 < count_profiles % 10 < 5:
                await message.answer(f'For your query was found {count_profiles} profile(s)')
            else:
                await message.answer(f'For your query was found {count_profiles} profile(s)')

        # Если пользователь ищет анкеты, чтобы просто поиграть
        if purpose in ['Просто поиграть', 'Just to play']:

            if user_language == '🇷🇺 Русский':
                text_just_play = f'Возраст: <b>{first_profile.age}</b>\n' \
                                 f'Пол: <b>{first_profile.gender}</b>\n' \
                                 f'Цель: <b>{first_profile.purpose}</b>\n' \
                                 f'Уровень игры: <b>{first_profile.play_level}</b>\n' \
                                 f'К/Д: <b>{first_profile.cool_down}</b>\n' \
                                 f'О себе: <b>{first_profile.about_yourself}</b>\n' \
                                 f'Играет в игры: <b>{games}</b>'
            else:
                text_just_play = f'Age: <b>{first_profile.age}</b>\n' \
                                 f'Gender: <b>{first_profile.gender}</b>\n' \
                                 f'Purpose: <b>{first_profile.purpose}</b>\n' \
                                 f'Level of play: <b>{first_profile.play_level}</b>\n' \
                                 f'Cool down: <b>{first_profile.cool_down}</b>\n' \
                                 f'About: <b>{first_profile.about_yourself}</b>\n' \
                                 f'Games: <b>{games}</b>'

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

            if user_language == '🇷🇺 Русский':
                text_real_life = f'{first_profile.name}, {first_profile.age} из {first_profile.country}\n' \
                                 f'Хобби: <b>{first_profile.hobby}</b>\n' \
                                 f'О себе: <b>{first_profile.about_yourself}</b>\n' \
                                 f'Играет в игры: <b>{games}</b>'
            else:
                text_real_life = f'{first_profile.name}, {first_profile.age} из {first_profile.country}\n' \
                                 f'Hobby: <b>{first_profile.hobby}</b>\n' \
                                 f'About: <b>{first_profile.about_yourself}</b>\n' \
                                 f'Games: <b>{games}</b>'

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
        if user_language == '🇷🇺 Русский':
            await message.answer('По вашим критериям поиска не нашлось анкет.\n\n'
                                 'Попробуйте поискать позднее или измените критерии поиска.')
        else:
            await message.answer('There were no questionnaires according to your search criteria.\n\n'
                                 'Try searching later or change the search criteria.')
