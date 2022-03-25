from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from keyboards.inline.gaming_keyboards import profile_action_target_keyboard, menu_my_profile_keyboard
from loader import dp, db
from utils.db_api import models
from keyboards.inline.gaming_keyboards import ru_button


# Сюда попадаем, когда пользователь нажал "zzz"
@dp.message_handler(state='zzz_second_user')
async def handler_zzz(message: types.Message, state: FSMContext):
    second_user_id = message.from_user.id
    second_user: models.User = await db.get_user(second_user_id)
    language_second_user = second_user.language
    option = message.text

    # Если пользователь выбрал вариант 1 "Показать профили, которым я нравлюсь"
    if option == '1':
        # Получаем всех пользователей, которые лайкнули анкету
        all_users_liked = await db.get_users_liked_my_profile(second_user_id)
        current_profile_liked_number = 0
        count_users_liked = len(all_users_liked)
        current_profile: models.User = all_users_liked[current_profile_liked_number]
        count_users_liked_for_text = count_users_liked - 1

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

        await state.set_state('in_like')

    # Если пользователь выбрал вариант 2 "Моя анкета"
    elif option == '2':

        game1 = second_user.game1
        game2 = second_user.game2

        if game1 is not None and game2 is not None:
            games = f'{game1}, {game2}'
        elif game2 is None:
            games = f'{game1}'
        elif game1 is None:
            games = f'{game2}'
        else:
            games = ''

        # Если текущий язык пользователя Русский
        if language_second_user == ru_button.text:

            text_ru = f'Имя: <b>{second_user.name}</b>\n' \
                      f'Возраст: <b>{second_user.age}</b>\n' \
                      f'Пол: <b>{second_user.gender}</b>\n' \
                      f'Ищу: <b>{second_user.purpose}</b>\n' \
                      f'Кого ищу: <b>{second_user.who_search}</b>\n' \
                      f'Страна: <b>{second_user.country}</b>\n' \
                      f'Город: <b>{second_user.city}</b>\n' \
                      f'О себе: <b>{second_user.about_yourself}</b>\n' \
                      f'Хобби: <b>{second_user.hobby}</b>\n' \
                      f'В какие игры играю: <b>{games}</b>'

            await message.answer('Ваш профиль:')

            if second_user.photo == 'None':
                await message.answer(text=text_ru)
            else:
                await message.answer_photo(photo=second_user.photo, caption=text_ru)

            await message.answer(text='1. Заполнить анкету заново\n'
                                      '2. Изменить фото\n'
                                      '3. Изменить текст анкеты\n'
                                      '4. Смотреть анкеты', reply_markup=menu_my_profile_keyboard)

        # Если текущий язык пользователя Английский
        else:
            text_en = f'Name: <b>{second_user.name}</b>\n' \
                      f'Age: <b>{second_user.age}</b>\n' \
                      f'Gender: <b>{second_user.gender}</b>\n' \
                      f'Search: <b>{second_user.purpose}</b>\n' \
                      f'Who search: <b>{second_user.who_search}</b>\n' \
                      f'Country: <b>{second_user.country}</b>\n' \
                      f'City: <b>{second_user.city}</b>\n' \
                      f'About yourself: <b>{second_user.about_yourself}</b>\n' \
                      f'Hobby: <b>{second_user.hobby}</b>\n' \
                      f'Playing games: <b>{games}</b>'

            await message.answer('Your profile:')

            if second_user.photo == 'None':
                await message.answer(text=text_en)
            else:
                await message.answer_photo(photo=second_user.photo, caption=text_en)

            await message.answer(text='1. Edit my profile\n'
                                      '2. Change my photo\n'
                                      '3. Change profile text\n'
                                      '4. View profiles', reply_markup=menu_my_profile_keyboard)

        await state.update_data(user_=second_user)
        await state.set_state('my_profile_state')

    # Если пользователь выбрал вариант 3 "Я больше не хочу никого искать"
    elif option == '3':
        # Если текущий язык пользователя Русский
        if language_second_user == ru_button.text:
            text_ru = 'Так ты не узнаешь, что кому-то нравишься... Точно хочешь отключить свою анкету?\n\n' \
                      '1. Да, отключить анкету.\n' \
                      '2. Нет, вернуться назад.'

            await message.answer(text=text_ru, reply_markup=ReplyKeyboardMarkup(keyboard=[
                [
                    KeyboardButton(text='1'),
                    KeyboardButton(text='2')
                ]
            ], resize_keyboard=True, one_time_keyboard=True))

        # Если текущий язык пользователя Английский
        else:
            text_en = "That way you won't know that someone likes you... " \
                      "Are you sure you want to disable your profile?\n\n" \
                      "1. Yes, disable the profile.\n" \
                      "2. No, go back."

            await message.answer(text=text_en, reply_markup=ReplyKeyboardMarkup(keyboard=[
                [
                    KeyboardButton(text='1'),
                    KeyboardButton(text='2')
                ]
            ], resize_keyboard=True, one_time_keyboard=True))

        await state.set_state('disable_second_profile')

    # Если пользователь не выбрал вариант, а что-то написал
    else:
        # Если текущий язык пользователя Русский
        if language_second_user == ru_button.text:
            await message.answer('Нет такого варианта ответа')

        # Если текущий язык пользователя Английский
        else:
            await message.answer('There is no such answer option')


# Сюда попадаем, когда пользователь нажал "zzz"
@dp.message_handler(state='zzz_second_user_send_message')
async def handler_zzz(message: types.Message, state: FSMContext):
    second_user_id = message.from_user.id
    second_user: models.User = await db.get_user(second_user_id)
    language_second_user = second_user.language
    option = message.text

    # Если пользователь выбрал вариант 1 "Показать профили, которым я нравлюсь"
    if option == '1':

        # Получаем всех пользователей, которые написали письмо
        all_users_send_message = await db.get_users_send_message(second_user_id)
        current_profile_send_message = 0
        count_users_send_message = len(all_users_send_message)
        current_profile: models.User = all_users_send_message[current_profile_send_message]
        count_users_send_message_for_text = count_users_send_message - 1

        await state.update_data(second_user=second_user,
                                all_users_send_message=all_users_send_message,
                                count_users_send_message=count_users_send_message,
                                current_profile_send_message=current_profile_send_message,
                                count_users_send_message_for_text=count_users_send_message_for_text)

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
            if count_users_send_message == 1:
                text = f'Кому-то понравилась твоя анкета:\n\n' \
                       f'{current_profile.name}, {current_profile.age} из {current_profile.country}\n' \
                       f'Хобби: <b>{current_profile.hobby}</b>\n' \
                       f'О себе: <b>{current_profile.about_yourself}</b>\n' \
                       f'Играет в игры: <b>{games}</b>' \
                       f'Письмо: <b>{current_profile.send_message_text}</b>'
            else:
                text = f'Кому-то понравилась твоя анкета (и ещё {count_users_send_message_for_text})\n\n' \
                       f'{current_profile.name}, {current_profile.age} из {current_profile.country}\n' \
                       f'Хобби: <b>{current_profile.hobby}</b>\n' \
                       f'О себе: <b>{current_profile.about_yourself}</b>\n' \
                       f'Играет в игры: <b>{games}</b>' \
                       f'Письмо: <b>{current_profile.send_message_text}</b>'

        else:
            if count_users_send_message == 1:
                text = f'Someone liked your profile:\n\n' \
                       f'{current_profile.name}, {current_profile.age} from {current_profile.country}\n' \
                       f'Hobby: <b>{current_profile.hobby}</b>\n' \
                       f'About: <b>{current_profile.about_yourself}</b>\n' \
                       f'Games: <b>{games}</b>' \
                       f'Message: <b>{current_profile.send_message_text}</b>'
            else:
                text = f'Someone liked your profile (and more {count_users_send_message_for_text})\n\n' \
                       f'{current_profile.name}, {current_profile.age} from {current_profile.country}\n' \
                       f'Hobby: <b>{current_profile.hobby}</b>\n' \
                       f'About: <b>{current_profile.about_yourself}</b>\n' \
                       f'Games: <b>{games}</b>' \
                       f'Message: <b>{current_profile.send_message_text}</b>'

        # Если пользователь без фото
        if photo == 'None':
            await message.answer(text=text, reply_markup=profile_action_target_keyboard)

        # Если пользователь с фото
        else:
            await message.answer_photo(photo=photo, caption=text, reply_markup=profile_action_target_keyboard)

        await state.set_state('in_send_message')

    # Если пользователь выбрал вариант 2 "Моя анкета"
    elif option == '2':

        game1 = second_user.game1
        game2 = second_user.game2

        if game1 is not None and game2 is not None:
            games = f'{game1}, {game2}'
        elif game2 is None:
            games = f'{game1}'
        elif game1 is None:
            games = f'{game2}'
        else:
            games = ''

        # Если текущий язык пользователя Русский
        if language_second_user == ru_button.text:

            text_ru = f'Имя: <b>{second_user.name}</b>\n' \
                      f'Возраст: <b>{second_user.age}</b>\n' \
                      f'Пол: <b>{second_user.gender}</b>\n' \
                      f'Ищу: <b>{second_user.purpose}</b>\n' \
                      f'Кого ищу: <b>{second_user.who_search}</b>\n' \
                      f'Страна: <b>{second_user.country}</b>\n' \
                      f'Город: <b>{second_user.city}</b>\n' \
                      f'О себе: <b>{second_user.about_yourself}</b>\n' \
                      f'Хобби: <b>{second_user.hobby}</b>\n' \
                      f'В какие игры играю: <b>{games}</b>'

            await message.answer('Ваш профиль:')

            if second_user.photo == 'None':
                await message.answer(text=text_ru)
            else:
                await message.answer_photo(photo=second_user.photo, caption=text_ru)

            await message.answer(text='1. Заполнить анкету заново\n'
                                      '2. Изменить фото\n'
                                      '3. Изменить текст анкеты\n'
                                      '4. Смотреть анкеты', reply_markup=menu_my_profile_keyboard)

        # Если текущий язык пользователя Английский
        else:
            text_en = f'Name: <b>{second_user.name}</b>\n' \
                      f'Age: <b>{second_user.age}</b>\n' \
                      f'Gender: <b>{second_user.gender}</b>\n' \
                      f'Search: <b>{second_user.purpose}</b>\n' \
                      f'Who search: <b>{second_user.who_search}</b>\n' \
                      f'Country: <b>{second_user.country}</b>\n' \
                      f'City: <b>{second_user.city}</b>\n' \
                      f'About yourself: <b>{second_user.about_yourself}</b>\n' \
                      f'Hobby: <b>{second_user.hobby}</b>\n' \
                      f'Playing games: <b>{games}</b>'

            await message.answer('Your profile:')

            if second_user.photo == 'None':
                await message.answer(text=text_en)
            else:
                await message.answer_photo(photo=second_user.photo, caption=text_en)

            await message.answer(text='1. Edit my profile\n'
                                      '2. Change my photo\n'
                                      '3. Change profile text\n'
                                      '4. View profiles', reply_markup=menu_my_profile_keyboard)

        await state.update_data(user_=second_user)
        await state.set_state('my_profile_state')

    # Если пользователь выбрал вариант 3 "Я больше не хочу никого искать"
    elif option == '3':
        # Если текущий язык пользователя Русский
        if language_second_user == ru_button.text:
            text_ru = 'Так ты не узнаешь, что кому-то нравишься... Точно хочешь отключить свою анкету?\n\n' \
                      '1. Да, отключить анкету.\n' \
                      '2. Нет, вернуться назад.'

            await message.answer(text=text_ru, reply_markup=ReplyKeyboardMarkup(keyboard=[
                [
                    KeyboardButton(text='1'),
                    KeyboardButton(text='2')
                ]
            ], resize_keyboard=True, one_time_keyboard=True))

        # Если текущий язык пользователя Английский
        else:
            text_en = "That way you won't know that someone likes you... " \
                      "Are you sure you want to disable your profile?\n\n" \
                      "1. Yes, disable the profile.\n" \
                      "2. No, go back."

            await message.answer(text=text_en, reply_markup=ReplyKeyboardMarkup(keyboard=[
                [
                    KeyboardButton(text='1'),
                    KeyboardButton(text='2')
                ]
            ], resize_keyboard=True, one_time_keyboard=True))

        await state.set_state('disable_second_profile')

    # Если пользователь не выбрал вариант, а что-то написал
    else:
        # Если текущий язык пользователя Русский
        if language_second_user == ru_button.text:
            await message.answer('Нет такого варианта ответа')

        # Если текущий язык пользователя Английский
        else:
            await message.answer('There is no such answer option')
