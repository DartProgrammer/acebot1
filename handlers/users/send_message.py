import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from keyboards.inline.gaming_keyboards import profile_action_target_keyboard, profile_action_like_keyboard
from loader import dp, bot, db, _
from utils.db_api import models


# Сюда попадаем, когда пользователь написал письмо, либо нажал "Вернуться назад"
@dp.message_handler(state='send_message')
async def send_message(message: types.Message, state: FSMContext):
    data = await state.get_data()

    profiles = data.get('profiles')
    count_profiles = data.get('count_profiles')
    current_profile_number = data.get('current_profile_number')
    current_profile: models.User = data.get('current_profile')

    game1_current_profile = current_profile.game1
    game2_current_profile = current_profile.game2

    if game1_current_profile is not None and game2_current_profile is not None:
        games_current_profile = f'{game1_current_profile}, {game2_current_profile}'
    elif game2_current_profile is None:
        games_current_profile = f'{game1_current_profile}'
    elif game1_current_profile is None:
        games_current_profile = f'{game2_current_profile}'
    else:
        games_current_profile = ''

    # Если пользователь нажал "Вернуться назад"
    if message.text == 'Вернуться назад' or message.text == 'Go back':
        text = _('{current_profile.name}, {current_profile.age} из {current_profile.country}\n'
                 'Хобби: <b>{current_profile.hobby}</b>\n'
                 'О себе: <b>{current_profile.about_yourself}</b>\n'
                 'Играет в игры: <b>{games_current_profile}</b>').format(current_profile=current_profile,
                                                                         games_current_profile=games_current_profile)

        if current_profile.photo == 'None':
            await message.answer(text=text, reply_markup=profile_action_target_keyboard)
        else:
            await message.answer_photo(photo=current_profile.photo, caption=text,
                                       reply_markup=profile_action_target_keyboard)

        await state.update_data(current_profile_number=current_profile_number)

        await state.set_state('find_profiles')

    # Если пользователь написал письмо
    else:
        text = message.text
        user_id_to_message = current_profile.user_id

        # Добавляем запись о письме в БД
        send_message_profiles = models.SendMessageProfiles(user_id=message.from_user.id,
                                                           profile_id=user_id_to_message,
                                                           send_message_text=text,
                                                           timestamp=datetime.datetime.now())
        await send_message_profiles.create()

        # Получаем всех пользователей, которые написали письмо
        all_users_send_message = await db.get_users_send_message(user_id_to_message)
        count_users_send_message = len(all_users_send_message)

        if count_users_send_message == 1:
            caption = _('Твоя анкета понравилась {count_users_send_message} пользователю, показать его?\n\n'
                        '1. Показать.\n'
                        '2. Не хочу больше никого смотреть.')
        elif count_users_send_message % 10 == 1:
            caption = _('Твоя анкета понравилась {count_users_send_message} пользователю, показать их?\n\n'
                        '1. Показать.\n'
                        '2. Не хочу больше никого смотреть.').format(count_users_send_message)
        else:
            caption = _('Твоя анкета понравилась {count_users_send_message} пользователям, показать их?\n\n'
                        '1. Показать.\n'
                        '2. Не хочу больше никого смотреть.').format(count_users_send_message)

        await bot.send_message(chat_id=user_id_to_message, text=caption, reply_markup=profile_action_like_keyboard)

        # Получаем состояние пользователя анкеты
        user_profile_state = dp.current_state(chat=user_id_to_message, user=user_id_to_message)

        # Изменяем состояние пользователя анкеты
        await user_profile_state.set_state('in_send_message')

        if current_profile_number + 1 < count_profiles:
            current_profile: models.User = profiles[current_profile_number + 1]

            text = _('{current_profile.name}, {current_profile.age} из {current_profile.country}\n'
                     'Хобби: <b>{current_profile.hobby}</b>\n'
                     'О себе: <b>{current_profile.about_yourself}</b>\n'
                     'Играет в игры: <b>{games_current_profile}</b>').format(current_profile=current_profile)

            if current_profile.photo == 'None':
                await message.answer(text=text, reply_markup=profile_action_target_keyboard)
            else:
                await message.answer_photo(photo=current_profile.photo, caption=text,
                                           reply_markup=profile_action_target_keyboard)

            await state.update_data(current_profile_number=current_profile_number + 1)

            await state.set_state('find_profiles')

        # Если профили закончились
        else:
            await message.answer(_('Профили по вашим критериям поиска закончились!\n'
                                   'Попробуйте повторить поиск позднее или изменить критерии поиска.'),
                                 reply_markup=ReplyKeyboardMarkup(keyboard=[
                                     [
                                         KeyboardButton(text=_('Главное меню'))
                                     ]
                                 ], resize_keyboard=True, one_time_keyboard=True))
