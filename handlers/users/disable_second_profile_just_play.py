from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from keyboards.inline.gaming_keyboards import menu_my_profile_keyboard
from loader import dp, _
from utils.db_api import models


# Попадаем сюда, когда пользователь выбрал вариант "Я больше не хочу никого искать"
# (из like_user_profile_just_play.py)
@dp.message_handler(state='disable_second_profile_just_play')
async def disable_profile_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user: models.User = data.get('second_user')
    option = message.text

    # Если пользователь выбрал вариант 1 "Да, отключить анкету"
    if option == '1':

        # Устанавливаем признак "Не активен" для профиля пользователя
        await user.update(enable=False).apply()

        await message.answer(_('Надеюсь, ты нашел кого-то благодаря мне! '
                               'Рад был с тобой пообщаться, будет скучно – пиши, '
                               'обязательно найдем тебе кого-нибудь 😉\n\n'
                               '1. Смотреть анкеты'),
                             reply_markup=ReplyKeyboardMarkup(keyboard=[
                                 [
                                     KeyboardButton(text=_('Смотреть анкеты'))
                                 ]
                             ], resize_keyboard=True, one_time_keyboard=True))

        await state.set_state('disable_second_profile_true_just_play')

    # Если пользователь выбрал вариант 2 "Нет, вернуться назад"
    elif option == '2':
        await message.answer(_('1. Показать профили, которым я нравлюсь\n'
                               '2. Моя анкета\n'
                               '3. Я больше не хочу никого искать'),
                             reply_markup=ReplyKeyboardMarkup(keyboard=[
                                 [
                                     KeyboardButton(text='1'),
                                     KeyboardButton(text='2'),
                                     KeyboardButton(text='3'),
                                 ]
                             ], resize_keyboard=True, one_time_keyboard=True))

        await state.set_state('zzz_just_play_second_user')

    # Если пользователь не выбрал вариант, а что-то написал
    else:
        await message.answer(_('Нет такого варианта ответа'))


# Попадаем сюда, когда пользователь выбрал вариант "Я больше не хочу никого искать"
# (из send_message_answer_just_play.py)
@dp.message_handler(state='disable_second_profile_send_message_just_play')
async def disable_profile_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user: models.User = data.get('second_user')
    option = message.text

    # Если пользователь выбрал вариант 1 "Да, отключить анкету"
    if option == '1':

        # Устанавливаем признак "Не активен" для профиля пользователя
        await user.update(enable=False).apply()

        await message.answer(_('Надеюсь, ты нашел кого-то благодаря мне! '
                               'Рад был с тобой пообщаться, будет скучно – пиши, '
                               'обязательно найдем тебе кого-нибудь 😉\n\n'
                               '1. Смотреть анкеты'),
                             reply_markup=ReplyKeyboardMarkup(keyboard=[
                                 [
                                     KeyboardButton(text=_('Смотреть анкеты'))
                                 ]
                             ], resize_keyboard=True, one_time_keyboard=True))

        await state.set_state('disable_second_profile_true_just_play')

    # Если пользователь выбрал вариант 2 "Нет, вернуться назад"
    elif option == '2':
        await message.answer(_('1. Показать профили, которым я нравлюсь\n'
                               '2. Моя анкета\n'
                               '3. Я больше не хочу никого искать'),
                             reply_markup=ReplyKeyboardMarkup(keyboard=[
                                 [
                                     KeyboardButton(text='1'),
                                     KeyboardButton(text='2'),
                                     KeyboardButton(text='3'),
                                 ]
                             ], resize_keyboard=True, one_time_keyboard=True))

        await state.set_state('zzz_just_play_second_user_send_message')

    # Если пользователь не выбрал вариант, а что-то написал
    else:
        await message.answer(_('Нет такого варианта ответа'))


# Попадаем сюда, если пользователь вновь захотел активировать свой профиль и нажал "Смотреть анкеты"
# (из like_user_profile_just_play.py)
@dp.message_handler(state='disable_second_profile_true_just_play')
async def enable_profile(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user: models.User = data.get('second_user')
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

    await state.update_data(user_=user)
    await state.set_state('my_profile_state')
