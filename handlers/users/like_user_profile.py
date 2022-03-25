from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from keyboards.inline.gaming_keyboards import profile_action_target_keyboard
from keyboards.inline.gaming_keyboards import ru_button
from loader import dp, bot, db
from utils.db_api import models


# Здесь ловим действия со стороны пользователя 2, когда пользователь 1 поставил лайк

# Если пользователь нажал 👍 (Показать)
@dp.message_handler(text='👍', state='in_like')
async def show_users_profiles(message: types.Message, state: FSMContext):
    second_user_id = message.from_user.id
    second_user: models.User = await db.get_user(second_user_id)
    language_second_user = second_user.language

    # Получаем всех пользователей, которые лайкнули анкету
    all_users_liked = await db.get_users_liked_my_profile(second_user_id)
    current_profile_liked_number = 0
    count_users_liked = len(all_users_liked)
    current_profile: models.User = all_users_liked[current_profile_liked_number]
    count_users_liked_for_text = count_users_liked - 1
    current_profile_liked: models.LikeProfiles = all_users_liked[current_profile_liked_number]

    # Устанавливаем у прочитанного сообщение признак "Прочитано"
    await db.setting_the_attribute_read_like_profiles(current_profile_liked[0])

    await state.update_data(second_user=second_user,
                            all_users_liked=all_users_liked,
                            count_users_liked=count_users_liked,
                            current_profile_liked_number=current_profile_liked_number,
                            count_users_liked_for_text=count_users_liked_for_text)

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

    if language_second_user == ru_button.text:
        # Изменяем текст в зависимости от количества лайков
        if count_users_liked == 1:
            text = f'Кому-то понравилась твоя анкета:\n\n' \
                   f'{current_profile.name}, {current_profile.age} из {current_profile.country}\n' \
                   f'Хобби: <b>{current_profile.hobby}</b>\n' \
                   f'О себе: <b>{current_profile.about_yourself}</b>\n' \
                   f'Играет в игры: <b>{games}</b>'

        else:
            text = f'Кому-то понравилась твоя анкета (и ещё {count_users_liked_for_text})\n\n' \
                   f'{current_profile.name}, {current_profile.age} из {current_profile.country}\n' \
                   f'Хобби: <b>{current_profile.hobby}</b>\n' \
                   f'О себе: <b>{current_profile.about_yourself}</b>\n' \
                   f'Играет в игры: <b>{games}</b>'

    else:
        if count_users_liked == 1:
            text = f'Someone liked your profile:\n\n' \
                   f'{current_profile.name}, {current_profile.age} from {current_profile.country}\n' \
                   f'Hobby: <b>{current_profile.hobby}</b>\n' \
                   f'About: <b>{current_profile.about_yourself}</b>\n' \
                   f'Games: <b>{games}</b>'
        else:
            text = f'Someone liked your profile (and more {count_users_liked_for_text})\n\n' \
                   f'{current_profile.name}, {current_profile.age} from {current_profile.country}\n' \
                   f'Hobby: <b>{current_profile.hobby}</b>\n' \
                   f'About: <b>{current_profile.about_yourself}</b>\n' \
                   f'Games: <b>{games}</b>'

    # Если пользователь без фото
    if photo == 'None':
        await message.answer(text=text, reply_markup=profile_action_target_keyboard)

    # Если пользователь с фото
    else:
        await message.answer_photo(photo=photo, caption=text, reply_markup=profile_action_target_keyboard)


# Если пользователь нажал 💤 (Не хочу больше никого смотреть)
@dp.message_handler(text='💤', state='in_like')
async def not_show_users_profiles(message: types.Message, state: FSMContext):
    second_user_id = message.from_user.id
    second_user: models.User = await db.get_user(second_user_id)
    language = second_user.language
    await state.update_data(second_user=second_user)

    if language == ru_button.text:
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

    await state.set_state('disable_second_profile')


# Если пользователь 2 нажал 💗
@dp.message_handler(text='💗', state='in_like')
async def like_user_profile(message: types.Message, state: FSMContext):
    data = await state.get_data()

    # Получаем информацию о пользователе
    second_user: models.User = data.get('second_user')
    # user_link = f'<a href="tg://user?id={second_user.user_id}">{second_user.name}</a>'
    user_link_username = f'<a href="https://t.me/{second_user.username}">{second_user.name}</a>'
    user_language = second_user.language

    # Получаем данные по найденным профилям
    all_users_liked = data.get('all_users_liked')
    count_users_liked = data.get('count_users_liked')
    current_profile_liked_number = data.get('current_profile_liked_number')
    count_users_liked_for_text = data.get('count_users_liked_for_text')
    current_profile: models.User = all_users_liked[current_profile_liked_number]
    current_profile_user_id = current_profile[1]
    # user_liked_link = f'<a href="tg://user?id={current_profile_user_id}">{current_profile.name}</a>'
    user_liked_link_username = f'<a href="https://t.me/{current_profile.username}">{current_profile.name}</a>'
    language_current_profile = current_profile.language

    # Отправляем информацию о взаимной симпатии пользователю 2
    if user_language == ru_button.text:
        # await message.answer(f'Есть взаимная симпатия! Начинай общаться 👉 {user_liked_link}')
        await message.answer(f'Есть взаимная симпатия! Начинай общаться 👉 {user_liked_link_username}',
                             disable_web_page_preview=True)
    else:
        # await message.answer(f'There is mutual sympathy! Start chatting 👉 {user_liked_link}')
        await message.answer(f'There is mutual sympathy! Start chatting 👉 {user_liked_link_username}',
                             disable_web_page_preview=True)

    # Если пользователь без фото
    if current_profile.photo == 'None':
        await message.answer(text=f'{current_profile.name}, {current_profile.age}, '
                                  f'{current_profile.city} - {current_profile.about_yourself}')

    # Если пользователь с фото
    else:
        await message.answer_photo(photo=current_profile.photo,
                                   caption=f'{current_profile.name}, {current_profile.age}, '
                                           f'{current_profile.city} - {current_profile.about_yourself}')

    # Отправляем информацию о взаимной симпатии пользователю 1
    if language_current_profile == ru_button.text:
        # await bot.send_message(chat_id=f'{current_profile_user_id}',
        #                        text=f'Есть взаимная симпатия! Начинай общаться 👉 {user_link}')
        await bot.send_message(chat_id=f'{current_profile_user_id}',
                               text=f'Есть взаимная симпатия! Начинай общаться 👉 {user_link_username}',
                               disable_web_page_preview=True)
    else:
        # await bot.send_message(chat_id=f'{current_profile_user_id}',
        #                        text=f'There is mutual sympathy! Start chatting 👉 {user_link}')
        await bot.send_message(chat_id=f'{current_profile_user_id}',
                               text=f'There is mutual sympathy! Start chatting 👉 {user_link_username}',
                               disable_web_page_preview=True)

    await bot.send_photo(chat_id=f'{current_profile_user_id}', photo=f'{second_user.photo}',
                         caption=f'{second_user.name}, {second_user.age}, {second_user.city} - '
                                 f'{second_user.about_yourself}')

    # Показываем пользователей, которым понравилась анкета
    if current_profile_liked_number + 1 < count_users_liked:
        current_profile: models.User = all_users_liked[current_profile_liked_number + 1]

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

        if user_language == ru_button.text:
            # Изменяем текст в зависимости от количества лайков
            if count_users_liked_for_text == 1:
                text = f'Кому-то понравилась твоя анкета:\n\n' \
                       f'{current_profile.name}, {current_profile.age} из {current_profile.country}\n' \
                       f'Хобби: <b>{current_profile.hobby}</b>\n' \
                       f'О себе: <b>{current_profile.about_yourself}</b>\n' \
                       f'Играет в игры: <b>{games}</b>'
            else:
                text = f'Кому-то понравилась твоя анкета (и ещё {count_users_liked_for_text})\n\n' \
                       f'{current_profile.name}, {current_profile.age} из {current_profile.country}\n' \
                       f'Хобби: <b>{current_profile.hobby}</b>\n' \
                       f'О себе: <b>{current_profile.about_yourself}</b>\n' \
                       f'Играет в игры: <b>{games}</b>'

        else:
            if count_users_liked_for_text == 1:
                text = f'Someone liked your profile:\n\n' \
                       f'{current_profile.name}, {current_profile.age} from {current_profile.country}\n' \
                       f'Hobby: <b>{current_profile.hobby}</b>\n' \
                       f'About: <b>{current_profile.about_yourself}</b>\n' \
                       f'Games: <b>{games}</b>'
            else:
                text = f'Someone liked your profile (and more {count_users_liked_for_text})\n\n' \
                       f'{current_profile.name}, {current_profile.age} from {current_profile.country}\n' \
                       f'Hobby: <b>{current_profile.hobby}</b>\n' \
                       f'About: <b>{current_profile.about_yourself}</b>\n' \
                       f'Games: <b>{games}</b>'

        # Если пользователь без фото
        if photo == 'None':
            await message.answer(text=text, reply_markup=profile_action_target_keyboard)

        # Если пользователь с фото
        else:
            await message.answer_photo(photo=photo, caption=text, reply_markup=profile_action_target_keyboard)

        await state.update_data(current_profile_liked_number=current_profile_liked_number + 1)

    # Сюда попадаем, когда показали всех пользователей, которым понравилась анкета
    else:
        if user_language == ru_button.text:
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


# Если пользователь 2 нажал 💌
@dp.message_handler(text='💌', state='in_like')
async def send_message_profile(message: types.Message, state: FSMContext):
    data = await state.get_data()

    # Получаем информацию о пользователе
    second_user: models.User = data.get('second_user')
    user_language = second_user.language

    if user_language == '🇷🇺 Русский':
        await message.answer('Напишите сообщение, которое хотите отправить')
    else:
        await message.answer('Write the message you want to send')

    await state.set_state('in_like_wait_answer')


# Если пользователь 2 нажал 👎
@dp.message_handler(text='👎', state='in_like')
async def dislike_user_profile(message: types.Message, state: FSMContext):
    data = await state.get_data()

    # Получаем информацию о пользователе
    second_user: models.User = data.get('second_user')
    user_language = second_user.language

    # Получаем данные по найденным профилям
    all_users_liked = data.get('all_users_liked')
    count_users_liked = data.get('count_users_liked')
    current_profile_liked_number = data.get('current_profile_liked_number')
    count_users_liked_for_text = data.get('count_users_liked_for_text')

    # Показываем пользователей, которым понравилась анкета
    if current_profile_liked_number + 1 < count_users_liked:
        current_profile: models.User = all_users_liked[current_profile_liked_number + 1]

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

        if user_language == '🇷🇺 Русский':
            # Изменяем текст в зависимости от количества лайков
            if count_users_liked_for_text == 1:
                text = f'Кому-то понравилась твоя анкета:\n\n' \
                       f'{current_profile.name}, {current_profile.age} из {current_profile.country}\n' \
                       f'Хобби: <b>{current_profile.hobby}</b>\n' \
                       f'О себе: <b>{current_profile.about_yourself}</b>\n' \
                       f'Играет в игры: <b>{games}</b>'
            else:
                text = f'Кому-то понравилась твоя анкета (и ещё {count_users_liked_for_text})\n\n' \
                       f'{current_profile.name}, {current_profile.age} из {current_profile.country}\n' \
                       f'Хобби: <b>{current_profile.hobby}</b>\n' \
                       f'О себе: <b>{current_profile.about_yourself}</b>\n' \
                       f'Играет в игры: <b>{games}</b>'

        else:
            if count_users_liked_for_text == 1:
                text = f'Someone liked your profile:\n\n' \
                       f'{current_profile.name}, {current_profile.age} from {current_profile.country}\n' \
                       f'Hobby: <b>{current_profile.hobby}</b>\n' \
                       f'About: <b>{current_profile.about_yourself}</b>\n' \
                       f'Games: <b>{games}</b>'
            else:
                text = f'Someone liked your profile (and more {count_users_liked_for_text})\n\n' \
                       f'{current_profile.name}, {current_profile.age} from {current_profile.country}\n' \
                       f'Hobby: <b>{current_profile.hobby}</b>\n' \
                       f'About: <b>{current_profile.about_yourself}</b>\n' \
                       f'Games: <b>{games}</b>'

        # Если пользователь без фото
        if photo == 'None':
            await message.answer(text=text, reply_markup=profile_action_target_keyboard)

        # Если пользователь с фото
        else:
            await message.answer_photo(photo=photo, caption=text, reply_markup=profile_action_target_keyboard)

        await state.update_data(current_profile_liked_number=current_profile_liked_number + 1)

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


# Сюда попадаем, когда пользователь 2 написал сообщение пользователю 1 (в ответ на лайк)
@dp.message_handler(state='in_like_wait_answer')
async def send_answer_message(message: types.Message, state: FSMContext):
    data = await state.get_data()

    # Получаем информацию о пользователе
    second_user: models.User = data.get('second_user')
    user_language = second_user.language
    # second_user_link = f'<a href="tg://user?id={second_user.user_id}">{second_user.name}</a>'
    second_user_link_username = f'<a href="https://t.me/{second_user.username}">{second_user.name}</a>'
    answer_text = message.text

    # Получаем данные по найденным профилям
    all_users_liked = data.get('all_users_liked')
    count_users_liked = data.get('count_users_liked')
    current_profile_liked_number = data.get('current_profile_liked_number')
    count_users_liked_for_text = data.get('count_users_liked_for_text')
    current_profile: models.User = all_users_liked[current_profile_liked_number]
    current_profile_user_id = current_profile[1]
    # user_liked_link = f'<a href="tg://user?id={current_profile_user_id}">{current_profile.name}</a>'
    user_liked_link_username = f'<a href="https://t.me/{current_profile.username}">{current_profile.name}</a>'
    language_current_profile = current_profile.language

    # Отправляем информацию о взаимной симпатии пользователю 2
    if user_language == '🇷🇺 Русский':
        await message.answer(f'Есть взаимная симпатия! Начинай общаться 👉 {user_liked_link_username}',
                             disable_web_page_preview=True)
    else:
        await message.answer(f'There is mutual sympathy! Start chatting 👉 {user_liked_link_username}',
                             disable_web_page_preview=True)

    # Если пользователь 1 без фото
    if current_profile.photo == 'None':
        await message.answer(text=f'{current_profile.name}, {current_profile.age}, '
                                  f'{current_profile.city} - {current_profile.about_yourself}')
    # Если пользователь 1 с фото
    else:
        await message.answer_photo(photo=current_profile.photo,
                                   caption=f'{current_profile.name}, {current_profile.age}, '
                                           f'{current_profile.city} - {current_profile.about_yourself}')

    # Отправляем информацию о взаимной симпатии пользователю 1
    if language_current_profile == '🇷🇺 Русский':
        await bot.send_message(chat_id=f'{current_profile_user_id}',
                               text=f'Есть взаимная симпатия! Начинай общаться 👉 {second_user_link_username}',
                               disable_web_page_preview=True)
    else:
        await bot.send_message(chat_id=f'{current_profile_user_id}',
                               text=f'There is mutual sympathy! Start chatting 👉 {second_user_link_username}',
                               disable_web_page_preview=True)

    text = f'{second_user.name}, {second_user.age}, {second_user.city} - {second_user.about_yourself}\n\n{answer_text}'
    # Если пользователь 2 без фото
    if second_user.photo == 'None':
        await bot.send_message(chat_id=f'{current_profile_user_id}', text=text)
    # Если пользователь 2 с фото
    else:
        await bot.send_photo(chat_id=f'{current_profile_user_id}', photo=f'{second_user.photo}', caption=text)

    # Показываем пользователей, которым понравилась анкета
    if current_profile_liked_number + 1 < count_users_liked:
        current_profile: models.User = all_users_liked[current_profile_liked_number + 1]

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

        if user_language == '🇷🇺 Русский':
            # Изменяем текст в зависимости от количества лайков
            if count_users_liked_for_text == 1:
                text = f'Кому-то понравилась твоя анкета:\n\n' \
                       f'{current_profile.name}, {current_profile.age} из {current_profile.country}\n' \
                       f'Хобби: <b>{current_profile.hobby}</b>\n' \
                       f'О себе: <b>{current_profile.about_yourself}</b>\n' \
                       f'Играет в игры: <b>{games}</b>'
            else:
                text = f'Кому-то понравилась твоя анкета (и ещё {count_users_liked_for_text})\n\n' \
                       f'{current_profile.name}, {current_profile.age} из {current_profile.country}\n' \
                       f'Хобби: <b>{current_profile.hobby}</b>\n' \
                       f'О себе: <b>{current_profile.about_yourself}</b>\n' \
                       f'Играет в игры: <b>{games}</b>'

        else:
            if count_users_liked_for_text == 1:
                text = f'Someone liked your profile:\n\n' \
                       f'{current_profile.name}, {current_profile.age} from {current_profile.country}\n' \
                       f'Hobby: <b>{current_profile.hobby}</b>\n' \
                       f'About: <b>{current_profile.about_yourself}</b>\n' \
                       f'Games: <b>{games}</b>'
            else:
                text = f'Someone liked your profile (and more {count_users_liked_for_text})\n\n' \
                       f'{current_profile.name}, {current_profile.age} from {current_profile.country}\n' \
                       f'Hobby: <b>{current_profile.hobby}</b>\n' \
                       f'About: <b>{current_profile.about_yourself}</b>\n' \
                       f'Games: <b>{games}</b>'

        # Если пользователь без фото
        if photo == 'None':
            await message.answer(text=text, reply_markup=profile_action_target_keyboard)

        # Если пользователь с фото
        else:
            await message.answer_photo(photo=photo, caption=text, reply_markup=profile_action_target_keyboard)

        await state.update_data(current_profile_liked_number=current_profile_liked_number + 1)

        await state.set_state('in_like')

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
