from aiogram import types
from aiogram.dispatcher import FSMContext, filters

from keyboards.inline.gaming_keyboards import menu_my_profile_keyboard
from loader import dp, db, _
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

        text_ru = _('Возраст: <b>{user.age}</b>\n'
                    'Пол: <b>{user.gender}</b>\n'
                    'Цель: <b>{user.purpose}</b>\n'
                    'Страна поиска: <b>{user.country}</b>\n'
                    'О себе: <b>{user.about_yourself}</b>\n'
                    'В какие игры играю: <b>{games}</b>\n'
                    'Уровень игры: <b>{user.play_level}</b>\n'
                    'Ваш К/Д: <b>{user.cool_down}</b>').format(user=user, games=games)

        await message.answer(_('Ваш профиль:'))
        if photo == 'None':
            await message.answer(text=text_ru)
        else:
            await message.answer_photo(photo=user.photo, caption=text_ru)
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
        await message.answer_photo(photo=user.photo, caption=text)
        await message.answer(text=_('1. Заполнить анкету заново\n'
                                    '2. Изменить фото\n'
                                    '3. Изменить текст анкеты\n'
                                    '4. Смотреть анкеты'), reply_markup=menu_my_profile_keyboard)

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
        await message.answer(_('Пришлите фото, не файл!'))
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
        text = _('Вот твой профиль:\n\n'
                 'Возраст: <b>{user.age}</b>\n'
                 'Пол: <b>{user.gender}</b>\n'
                 'Цель: <b>{user.purpose}</b>\n'
                 'Страна поиска: <b>{user.country}</b>\n'
                 'О себе: <b>{user.about_yourself}</b>\n'
                 'В какие игры играю: <b>{games}</b>\n'
                 'Уровень игры: <b>{user.play_level}</b>\n'
                 'Ваш К/Д: <b>{user.cool_down}</b>')

        await message.answer(_('Сохранили изменения, посмотрим как выглядит твоя анкета теперь'))

        if photo == 'None':
            await message.answer(text=text)
        else:
            await message.answer_photo(photo=link, caption=text)

        await message.answer(text=_('1. Заполнить анкету заново\n'
                                    '2. Изменить фото\n'
                                    '3. Изменить текст анкеты\n'
                                    '4. Смотреть анкеты'), reply_markup=menu_my_profile_keyboard)

    # Если цель поиска "Человека в реальной жизни" или "Команду для праков"
    else:
        text = _('Имя: <b>{user.name}</b>\n'
                 'Возраст: <b>{user.age}</b>\n'
                 'Пол: <b>{user.gender}</b>\n'
                 'Кого ищу: <b>{user.who_search}</b>\n'
                 'Страна: <b>{user.country}</b>\n'
                 'Город: <b>{user.city}</b>\n'
                 'О себе: <b>{user.about_yourself}</b>\n'
                 'Хобби: <b>{user.hobby}</b>\n'
                 'В какие игры играю: <b>{games}</b>').format(user=user, games=games)

        await message.answer(_('Сохранили изменения, посмотрим как выглядит твоя анкета теперь'))
        await message.answer_photo(photo=link, caption=text)
        await message.answer(text=_('1. Заполнить анкету заново\n'
                                    '2. Изменить фото\n'
                                    '3. Изменить текст анкеты\n'
                                    '4. Смотреть анкеты'), reply_markup=menu_my_profile_keyboard)

    await state.set_state('my_profile_state')
