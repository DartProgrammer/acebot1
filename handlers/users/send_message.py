import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from keyboards.inline.gaming_keyboards import profile_action_target_keyboard, profile_action_like_keyboard
from keyboards.inline.gaming_keyboards import ru_button
from loader import dp, bot, db
from utils.db_api import models


# Сюда попадаем, когда пользователь написал письмо, либо нажал "Вернуться назад"
@dp.message_handler(state='send_message')
async def send_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language')

    profiles = data.get('profiles')
    count_profiles = data.get('count_profiles')
    current_profile_number = data.get('current_profile_number')
    current_profile: models.User = data.get('current_profile')
    language_current_profile = current_profile.language

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
        # Если текущий язык пользователя Русский
        if language == ru_button.text:

            text_real_life = f'{current_profile.name}, {current_profile.age} из {current_profile.country}\n' \
                             f'Хобби: <b>{current_profile.hobby}</b>\n' \
                             f'О себе: <b>{current_profile.about_yourself}</b>\n' \
                             f'Играет в игры: <b>{games_current_profile}</b>'

            if current_profile.photo == 'None':
                await message.answer(text=text_real_life, reply_markup=profile_action_target_keyboard)
            else:
                await message.answer_photo(photo=current_profile.photo, caption=text_real_life,
                                           reply_markup=profile_action_target_keyboard)

        # Если текущий язык пользователя Английский
        else:

            text_real_life = f'{current_profile.name}, {current_profile.age} from {current_profile.country}\n' \
                             f'Hobby: <b>{current_profile.hobby}</b>\n' \
                             f'About: <b>{current_profile.about_yourself}</b>\n' \
                             f'Games: <b>{games_current_profile}</b>'

            if current_profile.photo == 'None':
                await message.answer(text=text_real_life, reply_markup=profile_action_target_keyboard)
            else:
                await message.answer_photo(photo=current_profile.photo, caption=text_real_life,
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

        # Если текущий язык анкеты пользователя Русский
        if language_current_profile == ru_button.text:
            if count_users_send_message == 1:
                caption = f'Твоя анкета понравилась {count_users_send_message} пользователю, показать его?\n\n' \
                          f'1. Показать.\n' \
                          f'2. Не хочу больше никого смотреть.'
            elif count_users_send_message % 10 == 1:
                caption = f'Твоя анкета понравилась {count_users_send_message} пользователю, показать их?\n\n' \
                          f'1. Показать.\n' \
                          f'2. Не хочу больше никого смотреть.'
            else:
                caption = f'Твоя анкета понравилась {count_users_send_message} пользователям, показать их?\n\n' \
                          f'1. Показать.\n' \
                          f'2. Не хочу больше никого смотреть.'

        # Если текущий язык анкеты пользователя Английский
        else:
            if count_users_send_message == 1:
                caption = f'{count_users_send_message} user liked your profile, should I show it?\n\n' \
                          f'1. Show.\n' \
                          f"2. I don't want to watch anyone."
            elif count_users_send_message % 10 == 1:
                caption = f'{count_users_send_message} users liked your profile, should I show them?\n\n' \
                          f'1. Show.\n' \
                          f"2. I don't want to watch anyone."
            else:
                caption = f'{count_users_send_message} users liked your profile, should I show them?\n\n' \
                          f'1. Show.\n' \
                          f"2. I don't want to watch anyone."

        await bot.send_message(chat_id=user_id_to_message, text=caption, reply_markup=profile_action_like_keyboard)

        # Получаем состояние пользователя анкеты
        user_profile_state = dp.current_state(chat=user_id_to_message, user=user_id_to_message)

        # Изменяем состояние пользователя анкеты
        await user_profile_state.set_state('in_send_message')

        if current_profile_number + 1 < count_profiles:
            current_profile: models.User = profiles[current_profile_number + 1]

            # Если текущий язык пользователя Русский
            if language == ru_button.text:
                text_real_life = f'{current_profile.name}, {current_profile.age} из {current_profile.country}\n' \
                                 f'Хобби: <b>{current_profile.hobby}</b>\n' \
                                 f'О себе: <b>{current_profile.about_yourself}</b>\n' \
                                 f'Играет в игры: <b>{games_current_profile}</b>'

                if current_profile.photo == 'None':
                    await message.answer(text=text_real_life, reply_markup=profile_action_target_keyboard)
                else:
                    await message.answer_photo(photo=current_profile.photo, caption=text_real_life,
                                               reply_markup=profile_action_target_keyboard)

            # Если текущий язык пользователя Английский
            else:
                text_real_life = f'{current_profile.name}, {current_profile.age} from {current_profile.country}\n' \
                                 f'Hobby: <b>{current_profile.hobby}</b>\n' \
                                 f'About: <b>{current_profile.about_yourself}</b>\n' \
                                 f'Games: <b>{games_current_profile}</b>'

                if current_profile.photo == 'None':
                    await message.answer(text=text_real_life, reply_markup=profile_action_target_keyboard)
                else:
                    await message.answer_photo(photo=current_profile.photo, caption=text_real_life,
                                               reply_markup=profile_action_target_keyboard)

            await state.update_data(current_profile_number=current_profile_number + 1)

            await state.set_state('find_profiles')

        # Если профили закончились
        else:
            if language == ru_button.text:
                await message.answer('Профили по вашим критериям поиска закончились!\n'
                                     'Попробуйте повторить поиск позднее или изменить критерии поиска.',
                                     reply_markup=ReplyKeyboardMarkup(keyboard=[
                                         [
                                             KeyboardButton(text='Главное меню')
                                         ]
                                     ], resize_keyboard=True, one_time_keyboard=True))
            else:
                await message.answer('Profiles based on your search criteria are over!\n'
                                     'Try to repeat the search later or change the search criteria.',
                                     reply_markup=ReplyKeyboardMarkup(keyboard=[
                                         [
                                             KeyboardButton(text='Main menu')
                                         ]
                                     ], resize_keyboard=True, one_time_keyboard=True))
