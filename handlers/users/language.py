from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Command

from keyboards.inline.gaming_keyboards import language_keyboard, menu_my_profile_keyboard
from loader import dp, _, db
from utils.db_api import models


@dp.message_handler(Command(['language']), state='*')
async def command_language(message: types.Message, state: FSMContext):
    await state.reset_state()
    user_id = message.from_user.id
    user: models.User = await db.get_user(user_id)

    await message.answer(_('Язык:'), reply_markup=language_keyboard)
    await state.update_data(user_=user)
    await state.set_state('set_language')


@dp.message_handler(state='set_language')
async def edit_language(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user: models.User = data.get('user_')
    language = message.text

    await state.update_data(language=language)
    await user.update(language=language).apply()

    purpose = user.purpose
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

        await message.answer(_('Ваш профиль:'))

        if photo == 'None':
            await message.answer(text=text)
        else:
            await message.answer_photo(photo=user.photo, caption=text)

        await message.answer(text=_('1. Заполнить анкету заново\n'
                                    '2. Изменить фото\n'
                                    '3. Изменить текст анкеты\n'
                                    '4. Смотреть анкеты'), reply_markup=menu_my_profile_keyboard)

    await state.set_state('my_profile_state')
