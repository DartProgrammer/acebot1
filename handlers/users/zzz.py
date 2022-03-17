from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from keyboards.inline.gaming_keyboards import profile_action_target_keyboard, menu_my_profile_keyboard
from loader import dp
from utils.db_api import models


# Сюда попадаем, когда пользователь нажал "zzz"
@dp.message_handler(state='zzz')
async def handler_zzz(message: types.Message, state: FSMContext):
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

            text_real_life_ru = f'{current_profile.name}, {current_profile.age} из {current_profile.country}\n' \
                                f'Хобби: <b>{current_profile.hobby}</b>\n' \
                                f'О себе: <b>{current_profile.about_yourself}</b>\n' \
                                f'Играет в игры: <b>{games}</b>'

            if current_profile.photo == 'None':
                await message.answer(text=text_real_life_ru, reply_markup=profile_action_target_keyboard)
            else:
                await message.answer_photo(photo=current_profile.photo, caption=text_real_life_ru,
                                           reply_markup=profile_action_target_keyboard)

            await state.update_data(current_profile_number=current_profile_number)

            await state.set_state('find_profiles')

        # Если пользователь выбрал вариант 2 "Моя анкета"
        elif option == '2':

            text_ru = f'Имя: <b>{user.name}</b>\n' \
                      f'Возраст: <b>{user.age}</b>\n' \
                      f'Пол: <b>{user.gender}</b>\n' \
                      f'Ищу: <b>{user.purpose}</b>\n' \
                      f'Кого ищу: <b>{user.who_search}</b>\n' \
                      f'Страна: <b>{user.country}</b>\n' \
                      f'Город: <b>{user.city}</b>\n' \
                      f'О себе: <b>{user.about_yourself}</b>\n' \
                      f'Хобби: <b>{user.hobby}</b>\n' \
                      f'В какие игры играю: <b>{games}</b>'

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

            await state.set_state('disable_profile')

        # Если пользователь не выбрал вариант, а что-то написал
        else:
            await message.answer('Нет такого варианта ответа')

    # Если текущий язык пользователя Английский
    else:

        # Если пользователь выбрал вариант 1 "View profiles"
        if option == '1 🔎':

            text_real_life_en = f'{current_profile.name}, {current_profile.age} из {current_profile.country}\n' \
                                f'Hobby: <b>{current_profile.hobby}</b>\n' \
                                f'About: <b>{current_profile.about_yourself}</b>\n' \
                                f'Games: <b>{games}</b>'

            if current_profile.photo == 'None':
                await message.answer(text=text_real_life_en, reply_markup=profile_action_target_keyboard)
            else:
                await message.answer_photo(photo=current_profile.photo, caption=text_real_life_en,
                                           reply_markup=profile_action_target_keyboard)

            await state.update_data(current_profile_number=current_profile_number)

            await state.set_state('find_profiles')

        # Если пользователь выбрал вариант 2 "My profile"
        elif option == '2':

            text_en = f'Name: <b>{user.name}</b>\n' \
                      f'Age: <b>{user.age}</b>\n' \
                      f'Gender: <b>{user.gender}</b>\n' \
                      f'Search: <b>{user.purpose}</b>\n' \
                      f'Who search: <b>{user.who_search}</b>\n' \
                      f'Country: <b>{user.country}</b>\n' \
                      f'City: <b>{user.city}</b>\n' \
                      f'About yourself: <b>{user.about_yourself}</b>\n' \
                      f'Hobby: <b>{user.hobby}</b>\n' \
                      f'Playing games: <b>{games}</b>'

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

            await state.set_state('disable_profile')

        # Если пользователь не выбрал вариант, а что-то написал
        else:
            await message.answer('There is no such answer option')
