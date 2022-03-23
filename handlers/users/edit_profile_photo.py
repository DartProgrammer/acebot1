from aiogram import types
from aiogram.dispatcher import FSMContext, filters

from keyboards.inline.gaming_keyboards import menu_my_profile_keyboard
from loader import dp, db
from utils.photo_link import photo_link
from utils.db_api import models


# Когда пользователь нажал "Вернуться назад"
@dp.message_handler(filters.Text(startswith=['Вернуться назад', 'Go back']), state='edit_profile_photo')
async def go_back(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = message.from_user.id
    user: models.User = await db.get_user(user_id)

    language = data.get('language')

    photo = user.photo
    purpose = user.purpose
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

        if language == '🇷🇺 Русский':
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

        if language == '🇷🇺 Русский':
            await message.answer('Ваш профиль:')
            await message.answer_photo(photo=user.photo, caption=text_ru)
            await message.answer(text='1. Заполнить анкету заново\n'
                                      '2. Изменить фото\n'
                                      '3. Изменить текст анкеты\n'
                                      '4. Смотреть анкеты', reply_markup=menu_my_profile_keyboard)
        else:
            await message.answer('Your profile:')
            await message.answer_photo(photo=user.photo, caption=text_en)
            await message.answer(text='1. Edit my profile\n'
                                      '2. Change my photo\n'
                                      '3. Change profile text\n'
                                      '4. View profiles', reply_markup=menu_my_profile_keyboard)

    await state.set_state('my_profile_state')


# Когда пользователь отправил новое фото для профиля
@dp.message_handler(state='edit_profile_photo', content_types=types.ContentTypes.ANY)
async def add_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = message.from_user.id
    user: models.User = await db.get_user(user_id)
    language = data.get('language')

    # Проверяем, что пользователь прислал фото, а не файл
    try:
        photo = message.photo[-1]

    except IndexError:
        if language == '🇷🇺 Русский':
            await message.answer('Пришлите фото, не файл!')
            return
        else:
            await message.answer('Send a photo, not a file!')
            return

    link = await photo_link(photo)
    await user.update(photo=link).apply()

    purpose = user.purpose
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

    # Если цель поиска "Просто поиграть"
    if purpose in ['Просто поиграть', 'Just to play']:

        text_ru = f'Вот твой профиль:\n\n' \
                  f'Возраст: <b>{user.age}</b>\n' \
                  f'Пол: <b>{user.gender}</b>\n' \
                  f'Цель: <b>{user.purpose}</b>\n' \
                  f'Страна поиска: <b>{user.country}</b>\n' \
                  f'О себе: <b>{user.about_yourself}</b>\n' \
                  f'В какие игры играю: <b>{games}</b>\n' \
                  f'Уровень игры: <b>{user.play_level}</b>\n' \
                  f'Ваш К/Д: <b>{user.cool_down}</b>'

        text_en = f'Here is your profile:\n\n' \
                  f'Age: <b>{user.age}</b>\n' \
                  f'Gender: <b>{user.gender}</b>\n' \
                  f'Purpose: <b>{user.purpose}</b>\n' \
                  f'Country teammates: <b>{user.country}</b>\n' \
                  f'About yourself: <b>{user.about_yourself}</b>\n' \
                  f'Playing games: <b>{games}</b>\n' \
                  f'Level of play: <b>{user.play_level}</b>\n' \
                  f'Your cool down: <b>{user.cool_down}</b>'

        if language == '🇷🇺 Русский':
            await message.answer('Сохранили изменения, посмотрим как выглядит твоя анкета теперь')

            if photo == 'None':
                await message.answer(text=text_ru)
            else:
                await message.answer_photo(photo=link, caption=text_ru)

            await message.answer(text='1. Заполнить анкету заново\n'
                                      '2. Изменить фото\n'
                                      '3. Изменить текст анкеты\n'
                                      '4. Смотреть анкеты', reply_markup=menu_my_profile_keyboard)
        else:
            await message.answer("Saved the changes, let's see what your profile looks like now")

            if photo == 'None':
                await message.answer(text=text_en)
            else:
                await message.answer_photo(photo=user.photo, caption=text_en)

            await message.answer(text='1. Edit my profile\n'
                                      '2. Change my photo\n'
                                      '3. Change profile text\n'
                                      '4. View profiles', reply_markup=menu_my_profile_keyboard)

    # Если цель поиска "Человека в реальной жизни" или "Команду для праков"
    else:
        text_ru = f'Имя: <b>{user.name}</b>\n' \
                  f'Возраст: <b>{user.age}</b>\n' \
                  f'Пол: <b>{user.gender}</b>\n' \
                  f'Кого ищу: <b>{user.who_search}</b>\n' \
                  f'Страна: <b>{user.country}</b>\n' \
                  f'Город: <b>{user.city}</b>\n' \
                  f'О себе: <b>{user.about_yourself}</b>\n' \
                  f'Хобби: <b>{user.hobby}</b>\n' \
                  f'В какие игры играю: <b>{games}</b>'

        text_en = f'Name: <b>{user.name}</b>\n' \
                  f'Age: <b>{user.age}</b>\n' \
                  f'Gender: <b>{user.gender}</b>\n' \
                  f'Who search: <b>{user.who_search}</b>\n' \
                  f'Country: <b>{user.country}</b>\n' \
                  f'City: <b>{user.city}</b>\n' \
                  f'About yourself: <b>{user.about_yourself}</b>\n' \
                  f'Hobby: <b>{user.hobby}</b>\n' \
                  f'Playing games: <b>{games}</b>'

        if language == '🇷🇺 Русский':
            await message.answer('Сохранили изменения, посмотрим как выглядит твоя анкета теперь')
            await message.answer_photo(photo=link, caption=text_ru)
            await message.answer(text='1. Заполнить анкету заново\n'
                                      '2. Изменить фото\n'
                                      '3. Изменить текст анкеты\n'
                                      '4. Смотреть анкеты', reply_markup=menu_my_profile_keyboard)
        else:
            await message.answer("Saved the changes, let's see what your profile looks like now")
            await message.answer_photo(photo=link, caption=text_en)
            await message.answer(text='1. Edit my profile\n'
                                      '2. Change my photo\n'
                                      '3. Change profile text\n'
                                      '4. View profiles', reply_markup=menu_my_profile_keyboard)

    await state.set_state('my_profile_state')
