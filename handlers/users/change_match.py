from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from keyboards.inline.gaming_keyboards import show_looking_for_keyboard, menu_my_profile_keyboard, get_teammates_country
from loader import dp, _, db
from utils.db_api import models


# Сюда попадаем, когда пользователь нажал "Изменить категорию поиска"
@dp.message_handler(Command(['change_match']), state='*')
async def profile_change_match(message: types.Message, state: FSMContext):
    await state.reset_state()
    user_id = message.from_user.id
    user: models.User = await db.get_user(user_id)
    age = user.age
    await state.update_data(user_=user)

    await message.answer(text=_('Кого ты ищешь?'), reply_markup=show_looking_for_keyboard(age))
    await state.set_state('change_match_looking_for')


# Изменяем категорию поиска пользователя и отправляем ему его анкету
@dp.message_handler(state='change_match_looking_for')
async def edit_looking_for(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user: models.User = data.get('user_')

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
        await message.answer(_('Из каких стран вы хотите, что бы были ваши тиммейты?'),
                             reply_markup=get_teammates_country())
        await state.set_state('just_play_after_change_match')

    # Если пользователь выбрал "Просто поиграть", и ранее он заполнял анкету по данной цели
    elif purpose in ['Просто поиграть', 'Just to play']:
        await message.answer(_('Ваш профиль:'))
        text = _('Возраст: <b>{age}</b>\n'
                 'Пол: <b>{gender}</b>\n'
                 'Цель: <b>{purpose}</b>\n'
                 'Страна поиска: <b>{country}</b>\n'
                 'О себе: <b>{about_yourself}</b>\n'
                 'В какие игры играю: <b>{games}</b>\n'
                 'Уровень игры: <b>{play_level}</b>\n'
                 'Ваш К/Д: <b>{cool_down}</b>').format(age=user.age, gender=user.gender, purpose=user.purpose,
                                                       country=user.country, about_yourself=user.about_yourself,
                                                       games=user.games, game1=user.game1, game2=user.game2)
        if photo == 'None':
            await message.answer(text=text)
        else:
            await message.answer_photo(photo=user.photo, caption=text)

        await message.answer(text=_('1. Заполнить анкету заново\n'
                                    '2. Изменить фото\n'
                                    '3. Изменить текст анкеты\n'
                                    '4. Смотреть анкеты'), reply_markup=menu_my_profile_keyboard)

        await state.set_state('my_profile_state')

    # Если пользователь выбрал "Команду для праков"
    elif purpose in ['Команду для праков', 'A team for practitioners']:
        await message.answer(_('Данная функция находится в стадии разработки'),
                             reply_markup=show_looking_for_keyboard(age))
        return
    # Если пользователь выбрал "Человека в реальной жизни"
    else:
        text = _('Имя: <b>{name}</b>\n'
                 'Возраст: <b>{age}</b>\n'
                 'Пол: <b>{gender}</b>\n'
                 'Ищу: <b>{purpose}</b>\n'
                 'Кого ищу: <b>{who_search}</b>\n'
                 'Страна: <b>{country}</b>\n'
                 'Город: <b>{city}</b>\n'
                 'О себе: <b>{about_yourself}</b>\n'
                 'Хобби: <b>{hobby}</b>\n'
                 'В какие игры играю: <b>{games}</b>').format(name=name, age=age, gender=gender, purpose=purpose,
                                                              who_search=who_search, country=country, city=city,
                                                              about_yourself=about_yourself, hobby=hobby, games=games)

        if photo == 'None':
            await message.answer(text=text)
        else:
            await message.answer_photo(photo=user.photo, caption=text)

        await message.answer(text=_('1. Заполнить анкету заново\n'
                                    '2. Изменить фото\n'
                                    '3. Изменить текст анкеты\n'
                                    '4. Смотреть анкеты'), reply_markup=menu_my_profile_keyboard)

        await state.set_state('my_profile_state')
