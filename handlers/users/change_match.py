from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from loader import db
from keyboards.inline.gaming_keyboards import show_looking_for_keyboard, menu_my_profile_keyboard, get_teammates_country
from keyboards.inline.gaming_keyboards import ru_button
from loader import dp
from utils.db_api import models


# Сюда попадаем, когда пользователь нажал "Изменить категорию поиска"
@dp.message_handler(Command(['change_match']), state='*')
async def profile_change_match(message: types.Message, state: FSMContext):
    await state.reset_state()
    user_id = message.from_user.id
    user: models.User = await db.get_user(user_id)
    language = user.language
    age = user.age
    await state.update_data(user_=user, language=language)

    text_ru = 'Кого ты ищешь?'
    text_en = 'Who are you looking for?'

    if language == ru_button.text:
        await message.answer(text=text_ru, reply_markup=show_looking_for_keyboard(language, age))
    else:
        await message.answer(text=text_en, reply_markup=show_looking_for_keyboard(language, age))

    await state.set_state('change_match_looking_for')


# Изменяем категорию поиска пользователя и отправляем ему его анкету
@dp.message_handler(state='change_match_looking_for')
async def edit_looking_for(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user: models.User = data.get('user_')
    language = data.get('language')

    purpose = message.text
    await state.update_data(purpose=purpose)

    await user.update(purpose=purpose).apply()

    name = user.name
    age = user.age
    gender = user.gender
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

    # Если пользователь выбрал "Просто поиграть", и ранее он не заполнял анкету по данной цели
    if purpose in ['Просто поиграть', 'Just to play'] and user.play_level == '':

        if language == ru_button.text:
            await message.answer('Из каких стран вы хотите, что бы были ваши тиммейты?',
                                 reply_markup=get_teammates_country(language))

        else:
            await message.answer('What countries do you want your teammates to be from?',
                                 reply_markup=get_teammates_country(language))

        await state.set_state('just_play_after_change_match')

    # Если пользователь выбрал "Просто поиграть", и ранее он заполнял анкету по данной цели
    elif purpose in ['Просто поиграть', 'Just to play']:

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

        await state.set_state('my_profile_state')

    # Если пользователь выбрал "Команду для праков"
    elif purpose in ['Команду для праков', 'A team for practitioners']:
        if language == ru_button.text:
            await message.answer('Данная функция находится в стадии разработки',
                                 reply_markup=show_looking_for_keyboard(language, age))
        else:
            await message.answer('This feature is under development',
                                 reply_markup=show_looking_for_keyboard(language, age))
        return
    # Если пользователь выбрал "Человека в реальной жизни"
    else:
        text_ru = f'Имя: <b>{name}</b>\n' \
                  f'Возраст: <b>{age}</b>\n' \
                  f'Пол: <b>{gender}</b>\n' \
                  f'Ищу: <b>{purpose}</b>\n' \
                  f'Кого ищу: <b>{who_search}</b>\n' \
                  f'Страна: <b>{country}</b>\n' \
                  f'Город: <b>{city}</b>\n' \
                  f'О себе: <b>{about_yourself}</b>\n' \
                  f'Хобби: <b>{hobby}</b>\n' \
                  f'В какие игры играю: <b>{games}</b>'

        text_en = f'Name: <b>{name}</b>\n' \
                  f'Age: <b>{age}</b>\n' \
                  f'Gender: <b>{gender}</b>\n' \
                  f'Search: <b>{purpose}</b>\n' \
                  f'Who search: <b>{who_search}</b>\n' \
                  f'Country: <b>{country}</b>\n' \
                  f'City: <b>{city}</b>\n' \
                  f'About yourself: <b>{about_yourself}</b>\n' \
                  f'Hobby: <b>{hobby}</b>\n' \
                  f'Playing games: <b>{games}</b>'

        if language == ru_button.text:
            if photo == 'None':
                await message.answer(text=text_ru)
            else:
                await message.answer_photo(photo=user.photo, caption=text_ru)

            await message.answer(text='1. Заполнить анкету заново\n'
                                      '2. Изменить фото\n'
                                      '3. Изменить текст анкеты\n'
                                      '4. Смотреть анкеты', reply_markup=menu_my_profile_keyboard)
        else:
            if photo == 'None':
                await message.answer(text=text_en)
            else:
                await message.answer_photo(photo=user.photo, caption=text_en)

            await message.answer(text='1. Edit my profile\n'
                                      '2. Change my photo\n'
                                      '3. Change profile text\n'
                                      '4. View profiles', reply_markup=menu_my_profile_keyboard)

        await state.set_state('my_profile_state')
