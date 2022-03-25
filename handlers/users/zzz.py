from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from keyboards.inline.gaming_keyboards import profile_action_target_keyboard, menu_my_profile_keyboard
from loader import dp, _
from utils.db_api import models


# Сюда попадаем, когда пользователь нажал "zzz"
@dp.message_handler(state='zzz')
async def handler_zzz(message: types.Message, state: FSMContext):
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
        text = _('{current_profile.name}, {current_profile.age} из {current_profile.country}\n'
                 'Хобби: <b>{current_profile.hobby}</b>\n'
                 'О себе: <b>{current_profile.about_yourself}</b>\n'
                 'Играет в игры: <b>{games}</b>').format(current_profile=current_profile, games=games)

        if current_profile.photo == 'None':
            await message.answer(text=text, reply_markup=profile_action_target_keyboard)
        else:
            await message.answer_photo(photo=current_profile.photo, caption=text,
                                       reply_markup=profile_action_target_keyboard)

        await state.update_data(current_profile_number=current_profile_number)

        await state.set_state('find_profiles')

    # Если пользователь выбрал вариант 2 "Моя анкета"
    elif option == '2':
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

        await state.set_state('disable_profile')

    # Если пользователь не выбрал вариант, а что-то написал
    else:
        await message.answer(_('Нет такого варианта ответа'))
