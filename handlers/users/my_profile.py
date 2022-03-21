import time

from aiogram import types
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.builtin import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from keyboards.inline.gaming_keyboards import menu_my_profile_keyboard, action_for_profile
from loader import dp, bot, db
from utils.db_api import models
from utils.db_api.db_commands import FindUsers

find_query = FindUsers()

keywords_my_profile = ['Изменить анкету', 'Edit profile', 'Главное меню', 'Main menu']


# Сюда попадаем, когда пользователь нажал "Моя анкета"(/my_profile) или "Изменить анкету"
@dp.message_handler(filters.Text(startswith=keywords_my_profile), state='*')
@dp.message_handler(Command(['my_profile']), state='*')
async def command_my_profile(message: types.Message, state: FSMContext):
    await state.reset_state()
    user_id = message.from_user.id
    user: models.User = await db.get_user(user_id)
    language = user.language
    await state.update_data(user_=user, language=language)
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

    photo = user.photo
    purpose = user.purpose

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


# Обрабатываем выдранный пользователем вариант действия
@dp.message_handler(state='my_profile_state')
async def edit_my_profile(message: types.Message, state: FSMContext):
    option = message.text
    data = await state.get_data()
    user: models.User = data.get('user_')
    language = data.get('language')
    purpose = user.purpose

    # Если текущий язык пользователя Русский
    if language == '🇷🇺 Русский':
        # Если пользователь выбрал вариант 1 "Заполнить анкету заново"
        if option == '1':
            await message.answer('Сколько тебе лет?', reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text=str(user.age))
                    ]
                ], resize_keyboard=True
            ))

            await state.set_state('edit_age')

        # Если пользователь выбрал вариант 2 "Изменить фото"
        elif option == '2':
            await message.answer('Пришли свое фото (не файл)', reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text='Вернуться назад')
                    ]
                ], resize_keyboard=True
            ))

            await state.set_state('edit_profile_photo')

        # Если пользователь выбрал вариант 3 "Изменить текст анкеты"
        elif option == '3':
            await message.answer('Расскажи о себе.', reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text='Вернуться назад')
                    ]
                ], resize_keyboard=True
            ))

            await state.set_state('edit_profile_description')

        # Если пользователь выбрал вариант 4 "Смотреть анкеты"
        elif option == '4 🔎':
            msg = await message.answer(f'Ищу подходящие анкеты 🔍')
            symbol1 = '🔎'
            symbol2 = '🔍'
            i = 0
            while i != 7:
                msg = await bot.edit_message_text(text=f'Ищу подходящие анкеты {symbol1}',
                                                  chat_id=message.from_user.id,
                                                  message_id=msg.message_id)

                time.sleep(.5)

                msg = await bot.edit_message_text(text=f'Ищу подходящие анкеты {symbol2}',
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

                if count_profiles % 10 == 1:
                    await message.answer(f'По вашему запросу найден {count_profiles} профиль')
                elif 1 < count_profiles % 10 < 5:
                    await message.answer(f'По вашему запросу найдено {count_profiles} профиля')
                else:
                    await message.answer(f'По вашему запросу найдено {count_profiles} профилей')

                # Если пользователь ищет анкеты, чтобы просто поиграть
                if purpose in ['Просто поиграть', 'Just to play']:

                    text_just_play_ru = f'Возраст: <b>{first_profile.age}</b>\n' \
                                        f'Пол: <b>{first_profile.gender}</b>\n' \
                                        f'Цель: <b>{first_profile.purpose}</b>\n' \
                                        f'Уровень игры: <b>{first_profile.play_level}</b>\n' \
                                        f'К/Д: <b>{first_profile.cool_down}</b>\n' \
                                        f'О себе: <b>{first_profile.about_yourself}</b>\n' \
                                        f'Играет в игры: <b>{games}</b>'

                    if first_profile.photo == 'None':
                        await message.answer(text=text_just_play_ru,
                                             reply_markup=action_for_profile(profiles=find_users,
                                                                             count_profiles=count_profiles,
                                                                             current_profile=0))
                    else:
                        await message.answer_photo(first_profile.photo,
                                                   caption=text_just_play_ru,
                                                   reply_markup=action_for_profile(profiles=find_users,
                                                                                   count_profiles=count_profiles,
                                                                                   current_profile=0))

                    await state.set_state('find_profiles_just_play')

                # Если пользователь ищет анкеты, чтобы познакомиться
                elif purpose in ['Человека в реальной жизни', 'A person in real life']:

                    text_real_life_ru = f'{first_profile.name}, {first_profile.age} из {first_profile.country}\n' \
                                        f'Хобби: <b>{first_profile.hobby}</b>\n' \
                                        f'О себе: <b>{first_profile.about_yourself}</b>\n' \
                                        f'Играет в игры: <b>{games}</b>'

                    if first_profile.photo == 'None':
                        await message.answer(text=text_real_life_ru,
                                             reply_markup=action_for_profile(profiles=find_users,
                                                                             count_profiles=count_profiles,
                                                                             current_profile=0))
                    else:
                        await message.answer_photo(first_profile.photo,
                                                   caption=text_real_life_ru,
                                                   reply_markup=action_for_profile(profiles=find_users,
                                                                                   count_profiles=count_profiles,
                                                                                   current_profile=0))

                    await state.set_state('find_profiles')

                await state.update_data(profiles=find_users,
                                        count_profiles=count_profiles,
                                        current_profile_number=0)

            except IndexError:
                await message.answer('По вашим критериям поиска не нашлось анкет.\n\n'
                                     'Попробуйте поискать позднее или измените критерии поиска.')

    # Если текущий язык пользователя Английский
    else:
        # Если пользователь выбрал вариант 1 "Edit my profile"
        if option == '1':
            await message.answer('How old are you?', reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text=str(user.age))
                    ]
                ], resize_keyboard=True
            ))

            await state.set_state('edit_age')

        # Если пользователь выбрал вариант 2 "Change my photo"
        elif option == '2':
            await message.answer('Send your photo (not file)', reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text='Go back')
                    ]
                ], resize_keyboard=True
            ))

            await state.set_state('edit_profile_photo')

        # Если пользователь выбрал вариант 3 "Change profile text"
        elif option == '3':
            await message.answer('Tell me about yourself.', reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text='Go back')
                    ]
                ], resize_keyboard=True
            ))

            await state.set_state('edit_profile_description')

        # Если пользователь выбрал вариант 4 "View profiles"
        elif option == '4 🔎':
            msg = await message.answer(f'Looking for suitable profiles 🔍')
            symbol1 = '🔎'
            symbol2 = '🔍'
            i = 0
            while i != 7:
                msg = await bot.edit_message_text(text=f'Looking for suitable profiles {symbol1}',
                                                  chat_id=message.from_user.id,
                                                  message_id=msg.message_id)

                time.sleep(.5)

                msg = await bot.edit_message_text(text=f'Looking for suitable profiles {symbol2}',
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

                if count_profiles % 10 == 1:
                    await message.answer(f'For your query was found {count_profiles} profile(s)')
                elif 1 < count_profiles % 10 < 5:
                    await message.answer(f'For your query was found {count_profiles} profile(s)')
                else:
                    await message.answer(f'For your query was found {count_profiles} profile(s)')

                # Если пользователь ищет анкеты, чтобы просто поиграть
                if purpose in ['Просто поиграть', 'Just to play']:

                    text_just_play_en = f'Age: <b>{first_profile.age}</b>\n' \
                                        f'Gender: <b>{first_profile.gender}</b>\n' \
                                        f'Purpose: <b>{first_profile.purpose}</b>\n' \
                                        f'Level of play: <b>{first_profile.play_level}</b>\n' \
                                        f'Cool down: <b>{first_profile.cool_down}</b>\n' \
                                        f'About: <b>{first_profile.about_yourself}</b>\n' \
                                        f'Games: <b>{games}</b>'

                    if first_profile.photo == 'None':
                        await message.answer(text=text_just_play_en,
                                             reply_markup=action_for_profile(profiles=find_users,
                                                                             count_profiles=count_profiles,
                                                                             current_profile=0))
                    else:
                        await message.answer_photo(first_profile.photo,
                                                   caption=text_just_play_en,
                                                   reply_markup=action_for_profile(profiles=find_users,
                                                                                   count_profiles=count_profiles,
                                                                                   current_profile=0))

                    await state.set_state('find_profiles_just_play')

                # Если пользователь ищет анкеты, чтобы познакомиться
                elif purpose in ['Человека в реальной жизни', 'A person in real life']:

                    text_real_life_en = f'{first_profile.name}, {first_profile.age} из {first_profile.country}\n' \
                                        f'Hobby: <b>{first_profile.hobby}</b>\n' \
                                        f'About: <b>{first_profile.about_yourself}</b>\n' \
                                        f'Games: <b>{games}</b>'

                    if first_profile.photo == 'None':
                        await message.answer(text=text_real_life_en,
                                             reply_markup=action_for_profile(profiles=find_users,
                                                                             count_profiles=count_profiles,
                                                                             current_profile=0))
                    else:
                        await message.answer_photo(first_profile.photo,
                                                   caption=text_real_life_en,
                                                   reply_markup=action_for_profile(profiles=find_users,
                                                                                   count_profiles=count_profiles,
                                                                                   current_profile=0))

                    await state.set_state('find_profiles')

                await state.update_data(profiles=find_users,
                                        count_profiles=count_profiles,
                                        current_profile_number=0)

            except IndexError:
                await message.answer('There were no questionnaires according to your search criteria.\n\n'
                                     'Try searching later or change the search criteria.')
