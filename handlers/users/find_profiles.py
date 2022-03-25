from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from keyboards.inline.gaming_keyboards import profile_action_target_keyboard, profile_action_like_keyboard
from loader import dp, bot, db, _
from utils.db_api import models


# Попадаем сюда, когда пользователь нажимает "Смотреть анкеты" и цель поиска "Человека в реальной жизни"
@dp.message_handler(state='find_profiles')
async def show_find_profiles(message: types.Message, state: FSMContext):
    data = await state.get_data()

    # Данные по найденным профилям
    profiles = data.get('profiles')
    count_profiles = data.get('count_profiles')
    current_profile_number = data.get('current_profile_number')

    current_profile: models.User = profiles[current_profile_number]
    language_current_profile = current_profile.language
    user_profile_id = current_profile.user_id

    # Данные пользователя, который ищет анкеты
    language = data.get('language')
    symbol = message.text

    # Если пользователь поставил лайк анкете
    if symbol == '💗':

        # Добавляем запись о лайке в БД
        await db.add_like_profile(user_profile_id)

        # Получаем всех пользователей, которые лайкнули анкету
        all_users_liked = await db.get_users_liked_my_profile(user_profile_id)
        count_users_liked = len(all_users_liked)

        if count_users_liked == 1:
            caption = _('Твоя анкета понравилась {count_users_liked} пользователю, показать его?\n\n'
                        '1. Показать.\n'
                        '2. Не хочу больше никого смотреть.').format(count_users_liked=count_users_liked)
        elif count_users_liked % 10 == 1:
            caption = _('Твоя анкета понравилась {count_users_liked} пользователю, показать их?\n\n'
                        '1. Показать.\n'
                        '2. Не хочу больше никого смотреть.').format(count_users_liked=count_users_liked)
        else:
            caption = _('Твоя анкета понравилась {count_users_liked} пользователям, показать их?\n\n'
                        '1. Показать.\n'
                        '2. Не хочу больше никого смотреть.')

        await bot.send_message(chat_id=user_profile_id, text=caption, reply_markup=profile_action_like_keyboard)

        # Получаем состояние пользователя анкеты
        user_profile_state = dp.current_state(chat=user_profile_id, user=user_profile_id)

        # Изменяем состояние пользователя анкеты
        await user_profile_state.set_state('in_like')

        # Проверяем, что профили не закончились
        if current_profile_number + 1 < count_profiles:
            current_profile: models.User = profiles[current_profile_number + 1]

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

            # Если текущий язык пользователя Русский
            text_real_life = _('{current_profile.name}, {current_profile.age} из {current_profile.country}\n'
                               'Хобби: <b>{current_profile.hobby}</b>\n'
                               'О себе: <b>{current_profile.about_yourself}</b>\n'
                               'Играет в игры: <b>{games_current_profile}</b>').format(current_profile,
                                                                                       games_current_profile)

            if current_profile.photo == 'None':
                await message.answer(text=text_real_life, reply_markup=profile_action_target_keyboard)
            else:
                await message.answer_photo(photo=current_profile.photo, caption=text_real_life,
                                           reply_markup=profile_action_target_keyboard)

            await state.update_data(current_profile_number=current_profile_number + 1)

        # Если профили закончились
        else:
            await message.answer(_('Профили по вашим критериям поиска закончились!\n'
                                   'Попробуйте повторить поиск позднее или изменить критерии поиска.'),
                                 reply_markup=ReplyKeyboardMarkup(keyboard=[
                                     [
                                         KeyboardButton(text=_('Главное меню'))
                                     ]
                                 ], resize_keyboard=True, one_time_keyboard=True))

    # Если пользователь хочет написать письмо профилю
    elif symbol == '💌':
        await message.answer(_('Напиши сообщение для этого пользователя'),
                             reply_markup=ReplyKeyboardMarkup(keyboard=[
                                 [
                                     KeyboardButton(text=_('Вернуться назад'))
                                 ]
                             ], resize_keyboard=True, one_time_keyboard=True))

        await state.update_data(current_profile=current_profile, current_profile_number=current_profile_number)
        await state.set_state('send_message')

    # Если пользователь поставил дизлайк анкете
    elif symbol == '👎':
        # Проверяем, что профили не закончились
        if current_profile_number + 1 < count_profiles:
            current_profile: models.User = profiles[current_profile_number + 1]

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

            text_real_life = _('{current_profile.name}, {current_profile.age} из {current_profile.country}\n'
                               'Хобби: <b>{current_profile.hobby}</b>\n'
                               'О себе: <b>{current_profile.about_yourself}</b>\n'
                               'Играет в игры: <b>{games_current_profile}</b>').format(current_profile=current_profile,
                                                                                       games_current_profile=games_current_profile)

            if current_profile.photo == 'None':
                await message.answer(text=text_real_life, reply_markup=profile_action_target_keyboard)
            else:
                await message.answer_photo(photo=current_profile.photo, caption=text_real_life,
                                           reply_markup=profile_action_target_keyboard)

            await state.update_data(current_profile_number=current_profile_number + 1)

        # Если профили закончились
        else:
            await message.answer(_('Профили по вашим критериям поиска закончились!\n'
                                   'Попробуйте повторить поиск позднее или изменить критерии поиска.'),
                                 reply_markup=ReplyKeyboardMarkup(keyboard=[
                                     [
                                         KeyboardButton(text=_('Главное меню'))
                                     ]
                                 ], resize_keyboard=True, one_time_keyboard=True))

    # Если пользователь нажал 'zzz'
    elif symbol == '💤':
        await message.answer(_('Подождем, пока кто-то увидит твою анкету'))
        await message.answer(_('1. Смотреть анкеты\n'
                               '2. Моя анкета\n'
                               '3. Я больше не хочу никого искать'),
                             reply_markup=ReplyKeyboardMarkup(keyboard=[
                                 [
                                     KeyboardButton(text='1 🔎'),
                                     KeyboardButton(text='2'),
                                     KeyboardButton(text='3'),
                                 ]
                             ], resize_keyboard=True, one_time_keyboard=True))

        await state.update_data(current_profile=current_profile, current_profile_number=current_profile_number)

        await state.set_state('zzz')

    # Если пользователь не нажал кнопку, а что-то написал
    else:
        await message.answer(_('Не знаю такой символ'))
