import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.builtin import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from keyboards.inline.gaming_keyboards import menu_my_profile_keyboard, action_for_profile
from loader import dp, bot, db, _
from utils.db_api import models
from utils.db_api.db_commands import FindUsers
from utils.range import async_range

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
        text = _('Возраст: <b>{user.age}</b>\n'
                 'Пол: <b>{user.gender}</b>\n'
                 'Цель: <b>{user.purpose}</b>\n'
                 'Страна поиска: <b>{user.country}</b>\n'
                 'О себе: <b>{user.about_yourself}</b>\n'
                 'В какие игры играю: <b>{games}</b>\n'
                 'Уровень игры: <b>{user.play_level}</b>\n'
                 'Ваш К/Д: <b>{user.cool_down}</b>').format(user=user, games=games)

        await message.answer(_('Ваш профиль:'))

        if photo == 'None':
            await message.answer(text=text)
        else:
            await message.answer_photo(photo=user.photo, caption=text)

        await message.answer(text=_('1. Заполнить анкету заново\n'
                                    '2. Изменить фото\n'
                                    '3. Изменить текст анкеты\n'
                                    '4. Смотреть анкеты'), reply_markup=menu_my_profile_keyboard)

    else:
        text = _('Имя: <b>{user.name}</b>\n'
                 'Возраст: <b>{user.age}</b>\n'
                 'Пол: <b>{user.gender}</b>\n'
                 'Ищу: <b>{user.purpose}</b>\n'
                 'Кого ищу: <b>{user.who_search}</b>\n'
                 'Страна: <b>{user.country}</b>\n'
                 'Город: <b>{user.city}</b>\n'
                 'О себе: <b>{user.about_yourself}</b>\n'
                 'Хобби: <b>{user.hobby}</b>\n'
                 'В какие игры играю: <b>{games}</b>').format(user=user, games=games)

        await message.answer('Ваш профиль:')

        if photo == 'None':
            await message.answer(text=text)
        else:
            await message.answer_photo(photo=user.photo, caption=text)

        await message.answer(text=_('1. Заполнить анкету заново\n'
                                    '2. Изменить фото\n'
                                    '3. Изменить текст анкеты\n'
                                    '4. Смотреть анкеты'), reply_markup=menu_my_profile_keyboard)

    await state.set_state('my_profile_state')


# Обрабатываем выдранный пользователем вариант действия
@dp.message_handler(state='my_profile_state')
async def edit_my_profile(message: types.Message, state: FSMContext):
    option = message.text
    data = await state.get_data()
    user: models.User = data.get('user_')
    purpose = user.purpose

    # Если пользователь выбрал вариант 1 "Заполнить анкету заново"
    if option == '1':
        await message.answer(_('Сколько тебе лет?'), reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=str(user.age))
                ]
            ], resize_keyboard=True
        ))

        await state.set_state('edit_age')

    # Если пользователь выбрал вариант 2 "Изменить фото"
    elif option == '2':
        await message.answer(_('Пришли свое фото (не файл)'), reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Вернуться назад')
                ]
            ], resize_keyboard=True
        ))

        await state.set_state('edit_profile_photo')

    # Если пользователь выбрал вариант 3 "Изменить текст анкеты"
    elif option == '3':
        await message.answer(_('Расскажи о себе.'), reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=_('Вернуться назад'))
                ]
            ], resize_keyboard=True
        ))

        await state.set_state('edit_profile_description')

    # Если пользователь выбрал вариант 4 "Смотреть анкеты"
    elif option == '4 🔎':
        msg = await message.answer(_('Ищу подходящие анкеты 🔍'))

        async for __ in await async_range(6):
            msg = await bot.edit_message_text(text=_('Ищу подходящие анкеты 🔎'),
                                              chat_id=message.from_user.id,
                                              message_id=msg.message_id)

            await asyncio.sleep(.5)

            msg = await bot.edit_message_text(text=_('Ищу подходящие анкеты 🔍'),
                                              chat_id=message.from_user.id,
                                              message_id=msg.message_id)

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
                await message.answer(_('По вашему запросу найден {count_profiles} профиль'))
            elif 1 < count_profiles % 10 < 5:
                await message.answer(_('По вашему запросу найдено {count_profiles} профиля'))
            else:
                await message.answer(_('По вашему запросу найдено {count_profiles} профилей'))

            # Если пользователь ищет анкеты, чтобы просто поиграть
            if purpose in ['Просто поиграть', 'Just to play']:

                text_just_play = _('Возраст: <b>{first_profile.age}</b>\n'
                                   'Пол: <b>{first_profile.gender}</b>\n'
                                   'Цель: <b>{first_profile.purpose}</b>\n'
                                   'Уровень игры: <b>{first_profile.play_level}</b>\n'
                                   'К/Д: <b>{first_profile.cool_down}</b>\n'
                                   'О себе: <b>{first_profile.about_yourself}</b>\n'
                                   'Играет в игры: <b>{games}</b>').format(first_profile=first_profile,
                                                                           games=games)

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
                text_real_life = _('{first_profile.name}, {first_profile.age} из {first_profile.country}\n'
                                   'Хобби: <b>{first_profile.hobby}</b>\n'
                                   'О себе: <b>{first_profile.about_yourself}</b>\n'
                                   'Играет в игры: <b>{games}</b>').format(first_profile=first_profile,
                                                                           games=games)

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

            await state.update_data(profiles=find_users,
                                    count_profiles=count_profiles,
                                    current_profile_number=0)

        except IndexError:
            await message.answer(_('По вашим критериям поиска не нашлось анкет.\n\n'
                                   'Попробуйте поискать позднее или измените критерии поиска.'))
