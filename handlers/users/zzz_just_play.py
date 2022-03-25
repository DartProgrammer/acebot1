from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from keyboards.inline.gaming_keyboards import profile_action_target_keyboard, menu_my_profile_keyboard
from loader import dp, _
from utils.db_api import models


# Сюда попадаем, когда пользователь нажал "zzz"
@dp.message_handler(state='zzz_just_play')
async def handler_zzz_just_play(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user: models.User = data.get('user_')
    language = data.get('language')
    option = message.text
    current_profile_number = data.get('current_profile_number')
    current_profile: models.User = data.get('current_profile')
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

    # Если пользователь выбрал вариант 1 "Смотреть анкеты"
    if option == '1 🔎':
        text = _('Возраст: <b>{current_profile.age}</b>\n'
                 'Пол: <b>{current_profile.gender}</b>\n'
                 'Цель: <b>{current_profile.purpose}</b>\n'
                 'Уровень игры: <b>{current_profile.play_level}</b>\n'
                 'К/Д: <b>{current_profile.cool_down}</b>\n'
                 'О себе: <b>{current_profile.about_yourself}</b>\n'
                 'Играет в игры: <b>{games}</b>').format(current_profile=current_profile, games=games)

        if current_profile.photo == 'None':
            await message.answer(text=text, reply_markup=profile_action_target_keyboard)
        else:
            await message.answer_photo(photo=current_profile.photo, caption=text,
                                       reply_markup=profile_action_target_keyboard)

        await state.update_data(current_profile_number=current_profile_number)

        await state.set_state('find_profiles_just_play')

    # Если пользователь выбрал вариант 2 "Моя анкета"
    elif option == '2':
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

        await state.set_state('my_profile_state')

    # Если пользователь выбрал вариант 3 "Я больше не хочу никого искать"
    elif option == '3':
        text_ru = _('Так ты не узнаешь, что кому-то нравишься... Точно хочешь отключить свою анкету?\n\n'
                    '1. Да, отключить анкету.\n'
                    '2. Нет, вернуться назад.')

        await message.answer(text=text_ru, reply_markup=ReplyKeyboardMarkup(keyboard=[
            [
                KeyboardButton(text='1'),
                KeyboardButton(text='2')
            ]
        ], resize_keyboard=True, one_time_keyboard=True))

        await state.set_state('disable_profile_just_play')

    # Если пользователь не выбрал вариант, а что-то написал
    else:
        await message.answer(_('Нет такого варианта ответа'))
