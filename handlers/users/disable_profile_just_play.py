from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from emoji import emojize

from keyboards.inline.gaming_keyboards import menu_my_profile_keyboard
from loader import dp
from utils.db_api import models


# Попадаем сюда, когда пользователь выбрал вариант "Я больше не хочу никого искать"
@dp.message_handler(state='disable_profile_just_play')
async def disable_profile_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user: models.User = data.get('user_')
    language = data.get('language')
    option = message.text

    # Если текущий язык пользователя Русский
    if language == '🇷🇺 Русский':

        # Если пользователь выбрал вариант 1 "Да, отключить анкету"
        if option == '1':

            # Устанавливаем признак "Не активен" для профиля пользователя
            await user.update(enable=False).apply()

            await message.answer(f'Надеюсь, ты нашел кого-то благодаря мне! '
                                 f'Рад был с тобой пообщаться, будет скучно – пиши, '
                                 f'обязательно найдем тебе кого-нибудь {emojize(":winking_face:")}\n\n'
                                 f'1. Смотреть анкеты',
                                 reply_markup=ReplyKeyboardMarkup(keyboard=[
                                     [
                                         KeyboardButton(text='Смотреть анкеты')
                                     ]
                                 ], resize_keyboard=True))

            await state.set_state('disable_profile_true_just_play')

        # Если пользователь выбрал вариант 2 "Нет, вернуться назад"
        elif option == '2':
            await message.answer('1. Смотреть анкеты\n'
                                 '2. Моя анкета\n'
                                 '3. Я больше не хочу никого искать',
                                 reply_markup=ReplyKeyboardMarkup(keyboard=[
                                     [
                                         KeyboardButton(text='1 🔎'),
                                         KeyboardButton(text='2'),
                                         KeyboardButton(text='3'),
                                     ]
                                 ], resize_keyboard=True))

            await state.set_state('zzz_just_play')

        # Если пользователь не выбрал вариант, а что-то написал
        else:
            await message.answer('Нет такого варианта ответа')

    # Если текущий язык пользователя Английский
    else:

        # Если пользователь выбрал вариант 1 "Yes, disable the profile"
        if option == '1':

            # Устанавливаем признак "Не активен" для профиля пользователя
            await user.update(enable=False).apply()

            await message.answer(f'I hope you found someone thanks to me! I was glad to talk to you, '
                                 f'it will be boring - write, we will definitely find someone for you '
                                 f'{emojize(":winking_face:")}\n\n'
                                 f'1. View profiles',
                                 reply_markup=ReplyKeyboardMarkup(keyboard=[
                                     [
                                         KeyboardButton(text='View profiles')
                                     ]
                                 ], resize_keyboard=True))

            await state.set_state('disable_profile_true_just_play')

        # Если пользователь выбрал вариант 2 "No, go back"
        elif option == '2':
            await message.answer("1. View profiles\n"
                                 "2. My profile\n"
                                 "3. I don't want to look for anyone anymore",
                                 reply_markup=ReplyKeyboardMarkup(keyboard=[
                                     [
                                         KeyboardButton(text='1 🔎'),
                                         KeyboardButton(text='2'),
                                         KeyboardButton(text='3'),
                                     ]
                                 ], resize_keyboard=True))

            await state.set_state('zzz_just_play')

        # Если пользователь не выбрал вариант, а что-то написал
        else:
            await message.answer('There is no such answer option')


# Попадаем сюда, если пользователь вновь захотел активировать свой профиль и нажал "Смотреть анкеты"
@dp.message_handler(state='disable_profile_true_just_play')
async def enable_profile(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user: models.User = data.get('user_')
    language = data.get('language')
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

    # Устанавливаем признак "Активен" для профиля пользователя
    await user.update(enable=True).apply()

    # Если текущий язык пользователя Русский
    if language == '🇷🇺 Русский':

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

    # Если текущий язык пользователя Английский
    else:

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

    await state.update_data(user_=user)
    await state.set_state('my_profile_state')
