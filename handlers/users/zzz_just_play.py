from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from keyboards.inline.gaming_keyboards import profile_action_target_keyboard, menu_my_profile_keyboard
from loader import dp
from utils.db_api import models


# Сюда попадаем, когда пользователь нажал "zzz"
@dp.message_handler(state='zzz_just_play')
async def handler_zzz_just_play(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user: models.User = data.get('user_')
    language = data.get('language')
    option = message.text
    current_profile_number = data.get('current_profile_number')
    current_profile: models.User = data.get('current_profile')
    photo = user.photo
    game1 = user.game1
    game2 = user.game2

    if game1 == '' and game2 == '':
        games = f'{game1}, {game2}'
    elif game2 == '':
        games = f'{game1}'
    elif game1 == '':
        games = f'{game2}'
    else:
        games = ''

    # Если текущий язык пользователя Русский
    if language == '🇷🇺 Русский':

        # Если пользователь выбрал вариант 1 "Смотреть анкеты"
        if option == '1 🔎':

            text_just_play_ru = f'Возраст: <b>{current_profile.age}</b>\n' \
                                f'Пол: <b>{current_profile.gender}</b>\n' \
                                f'Цель: <b>{current_profile.purpose}</b>\n' \
                                f'Уровень игры: <b>{current_profile.play_level}</b>\n' \
                                f'К/Д: <b>{current_profile.cool_down}</b>\n' \
                                f'О себе: <b>{current_profile.about_yourself}</b>\n' \
                                f'Играет в игры: <b>{games}</b>'

            if current_profile.photo == 'None':
                await message.answer(text=text_just_play_ru, reply_markup=profile_action_target_keyboard)
            else:
                await message.answer_photo(photo=current_profile.photo, caption=text_just_play_ru,
                                           reply_markup=profile_action_target_keyboard)

            await state.update_data(current_profile_number=current_profile_number)

            await state.set_state('find_profiles_just_play')

        # Если пользователь выбрал вариант 2 "Моя анкета"
        elif option == '2':

            text_ru = f'Возраст: <b>{user.age}</b>\n' \
                      f'Пол: <b>{user.gender}</b>\n' \
                      f'Цель: <b>{user.purpose}</b>\n' \
                      f'Страна поиска: <b>{user.country}</b>\n' \
                      f'О себе: <b>{user.about_yourself}</b>\n' \
                      f'В какие игры играю: <b>{games}</b>\n' \
                      f'Уровень игры: <b>{user.play_level}</b>\n' \
                      f'Ваш К/Д: <b>{user.cool_down}</b>'

            await message.answer('Ваш профиль:')

            if photo == 'None':
                await message.answer(text=text_ru)
            else:
                await message.answer_photo(photo=user.photo, caption=text_ru)

            await message.answer(text='1. Заполнить анкету заново\n'
                                      '2. Изменить фото\n'
                                      '3. Изменить текст анкеты\n'
                                      '4. Смотреть анкеты', reply_markup=menu_my_profile_keyboard)

            await state.set_state('my_profile_state')

        # Если пользователь выбрал вариант 3 "Я больше не хочу никого искать"
        elif option == '3':
            text_ru = 'Так ты не узнаешь, что кому-то нравишься... Точно хочешь отключить свою анкету?\n\n' \
                      '1. Да, отключить анкету.\n' \
                      '2. Нет, вернуться назад.'

            await message.answer(text=text_ru, reply_markup=ReplyKeyboardMarkup(keyboard=[
                [
                    KeyboardButton(text='1'),
                    KeyboardButton(text='2')
                ]
            ], resize_keyboard=True, one_time_keyboard=True))

            await state.set_state('disable_profile_just_play')

        # Если пользователь не выбрал вариант, а что-то написал
        else:
            await message.answer('Нет такого варианта ответа')

    # Если текущий язык пользователя Английский
    else:

        # Если пользователь выбрал вариант 1 "View profiles"
        if option == '1 🔎':

            text_just_play_en = f'Age: <b>{current_profile.age}</b>\n' \
                                f'Gender: <b>{current_profile.gender}</b>\n' \
                                f'Purpose: <b>{current_profile.purpose}</b>\n' \
                                f'Level of play: <b>{current_profile.play_level}</b>\n' \
                                f'Cool down: <b>{current_profile.cool_down}</b>\n' \
                                f'About: <b>{current_profile.about_yourself}</b>\n' \
                                f'Games: <b>{games}</b>'

            if current_profile.photo == 'None':
                await message.answer(text=text_just_play_en, reply_markup=profile_action_target_keyboard)
            else:
                await message.answer_photo(photo=current_profile.photo, caption=text_just_play_en,
                                           reply_markup=profile_action_target_keyboard)

            await state.update_data(current_profile_number=current_profile_number)

            await state.set_state('find_profiles_just_play')

        # Если пользователь выбрал вариант 2 "My profile"
        elif option == '2':

            text_en = f'Age: <b>{user.age}</b>\n' \
                      f'Gender: <b>{user.gender}</b>\n' \
                      f'Purpose: <b>{user.purpose}</b>\n' \
                      f'Country teammates: <b>{user.country}</b>\n' \
                      f'About yourself: <b>{user.about_yourself}</b>\n' \
                      f'Playing games: <b>{games}</b>\n' \
                      f'Level of play: <b>{user.play_level}</b>\n' \
                      f'Your cool down: <b>{user.cool_down}</b>'

            await message.answer('Your profile:')

            if photo == 'None':
                await message.answer(text=text_en)
            else:
                await message.answer_photo(photo=user.photo, caption=text_en)

            await message.answer(text='1. Edit my profile\n'
                                      '2. Change my photo\n'
                                      '3. Change profile text\n'
                                      '4. View profiles', reply_markup=menu_my_profile_keyboard)

            await state.set_state('my_profile_state')

        # Если пользователь выбрал вариант 3 "I don't want to look for anyone anymore"
        elif option == '3':
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

            await state.set_state('disable_profile_just_play')

        # Если пользователь не выбрал вариант, а что-то написал
        else:
            await message.answer('There is no such answer option')
