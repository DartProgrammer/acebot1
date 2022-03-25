from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Command

from keyboards.inline.gaming_keyboards import language_keyboard, menu_language_keyboard, menu_my_profile_keyboard
from keyboards.inline.gaming_keyboards import ru_button
from loader import dp
from utils.db_api import models
from utils.db_api.db_commands import DBCommands

db = DBCommands()


@dp.message_handler(Command(['language']), state='*')
async def command_language(message: types.Message, state: FSMContext):
    await state.reset_state()
    user_id = message.from_user.id
    user: models.User = await db.get_user(user_id)
    language = user.language

    if language == ru_button.text:
        await message.answer('Язык:', reply_markup=language_keyboard)
    else:
        await message.answer('Language:', reply_markup=language_keyboard)

    await state.update_data(user_=user)
    await state.set_state('set_language')


@dp.message_handler(state='set_language')
async def edit_language(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user: models.User = data.get('user_')
    language = message.text

    await state.update_data(language=language)
    await user.update(language=language).apply()

    name = user.name
    age = user.age
    gender = user.gender
    purpose = user.purpose
    who_search = user.who_search
    country = user.country
    city = user.city
    about_yourself = user.about_yourself
    hobby = user.hobby
    photo = user.photo
    game1 = user.game1
    game2 = user.game2

    if game1 is not None and game2 is not None:
        games = f'{game1}, {game2}'
    elif game2 is None:
        games = f'{game1}'
    elif game1 is None:
        games = f'{game2}'
    else:
        games = ''

    if purpose in ['Просто поиграть', 'Just to play']:

        text_ru = f'Возраст: <b>{user.age}</b>\n' \
                  f'Пол: <b>{user.gender}</b>\n' \
                  f'Цель: <b>{user.purpose}</b>\n' \
                  f'Страна поиска: <b>{user.country}</b>\n' \
                  f'О себе: <b>{user.about_yourself}</b>\n' \
                  f'В какие игры играю: <b>{games}</b>\n' \
                  f'Уровень игры: <b>{user.play_level}</b>\n' \
                  f'Ваш К/Д: <b>{user.cool_down}</b>'

        text_en = f'Age: <b>{user.age}</b>\n' \
                  f'Gender: <b>{user.gender}</b>\n' \
                  f'Purpose: <b>{user.purpose}</b>\n' \
                  f'Country teammates: <b>{user.country}</b>\n' \
                  f'About yourself: <b>{user.about_yourself}</b>\n' \
                  f'Playing games: <b>{games}</b>\n' \
                  f'Level of play: <b>{user.play_level}</b>\n' \
                  f'Your cool down: <b>{user.cool_down}</b>'

        if language == ru_button.text:
            await message.answer('Ваш профиль:')

            if photo == 'None':
                await message.answer(text=text_ru)
            else:
                await message.answer_photo(photo=user.photo, caption=text_ru)

            await message.answer(text='1. Заполнить анкету заново\n'
                                      '2. Изменить фото\n'
                                      '3. Изменить текст анкеты\n'
                                      '4. Смотреть анкеты', reply_markup=menu_my_profile_keyboard)
        else:
            await message.answer('Your profile:')

            if photo == 'None':
                await message.answer(text=text_en)
            else:
                await message.answer_photo(photo=user.photo, caption=text_en)

            await message.answer(text='1. Edit my profile\n'
                                      '2. Change my photo\n'
                                      '3. Change profile text\n'
                                      '4. View profiles', reply_markup=menu_my_profile_keyboard)

    else:
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

        if language == ru_button.text:
            await message.answer('Ваш профиль:')

            if photo == 'None':
                await message.answer(text=text_ru)
            else:
                await message.answer_photo(photo=user.photo, caption=text_ru)

            await message.answer(text='1. Заполнить анкету заново\n'
                                      '2. Изменить фото\n'
                                      '3. Изменить текст анкеты\n'
                                      '4. Смотреть анкеты', reply_markup=menu_my_profile_keyboard)
        else:
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
