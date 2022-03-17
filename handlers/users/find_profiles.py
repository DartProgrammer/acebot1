from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from handlers.users.start import db
from keyboards.inline.gaming_keyboards import profile_action_target_keyboard, profile_action_like_keyboard
from loader import dp, bot
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

        # Если текущий язык анкеты пользователя Русский
        if language_current_profile == '🇷🇺 Русский':
            if count_users_liked == 1:
                caption = f'Твоя анкета понравилась {count_users_liked} пользователю, показать его?\n\n' \
                          f'1. Показать.\n' \
                          f'2. Не хочу больше никого смотреть.'
            elif count_users_liked % 10 == 1:
                caption = f'Твоя анкета понравилась {count_users_liked} пользователю, показать их?\n\n' \
                          f'1. Показать.\n' \
                          f'2. Не хочу больше никого смотреть.'
            else:
                caption = f'Твоя анкета понравилась {count_users_liked} пользователям, показать их?\n\n' \
                          f'1. Показать.\n' \
                          f'2. Не хочу больше никого смотреть.'

        # Если текущий язык анкеты пользователя Английский
        else:
            if count_users_liked == 1:
                caption = f'{count_users_liked} user liked your profile, should I show it?\n\n' \
                          f'1. Show.\n' \
                          f"2. I don't want to watch anyone."
            elif count_users_liked % 10 == 1:
                caption = f'{count_users_liked} users liked your profile, should I show them?\n\n' \
                          f'1. Show.\n' \
                          f"2. I don't want to watch anyone."
            else:
                caption = f'{count_users_liked} users liked your profile, should I show them?\n\n' \
                          f'1. Show.\n' \
                          f"2. I don't want to watch anyone."

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
            if language == '🇷🇺 Русский':
                text_real_life = f'{current_profile.name}, {current_profile.age} из {current_profile.country}\n' \
                                 f'Хобби: <b>{current_profile.hobby}</b>\n' \
                                 f'О себе: <b>{current_profile.about_yourself}</b>\n' \
                                 f'Играет в игры: <b>{games_current_profile}</b>'

            # Если текущий язык пользователя Английский
            else:
                text_real_life = f'{current_profile.name}, {current_profile.age} из {current_profile.country}\n' \
                                 f'Hobby: <b>{current_profile.hobby}</b>\n' \
                                 f'About: <b>{current_profile.about_yourself}</b>\n' \
                                 f'Games: <b>{games_current_profile}</b>'

            if current_profile.photo == 'None':
                await message.answer(text=text_real_life, reply_markup=profile_action_target_keyboard)
            else:
                await message.answer_photo(photo=current_profile.photo, caption=text_real_life,
                                           reply_markup=profile_action_target_keyboard)

            await state.update_data(current_profile_number=current_profile_number + 1)

        # Если профили закончились
        else:
            if language == '🇷🇺 Русский':
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

    # Если пользователь хочет написать письмо профилю
    elif symbol == '💌':
        # Если текущий язык пользователя Русский
        if language == '🇷🇺 Русский':
            await message.answer('Напиши сообщение для этого пользователя',
                                 reply_markup=ReplyKeyboardMarkup(keyboard=[
                                     [
                                         KeyboardButton(text='Вернуться назад')
                                     ]
                                 ], resize_keyboard=True, one_time_keyboard=True))

        # Если текущий язык пользователя Английский
        else:
            await message.answer('Write a message for this user',
                                 reply_markup=ReplyKeyboardMarkup(keyboard=[
                                     [
                                         KeyboardButton(text='Go back')
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

            # Если текущий язык пользователя Русский
            if language == '🇷🇺 Русский':
                text_real_life = f'{current_profile.name}, {current_profile.age} из {current_profile.country}\n' \
                                 f'Хобби: <b>{current_profile.hobby}</b>\n' \
                                 f'О себе: <b>{current_profile.about_yourself}</b>\n' \
                                 f'Играет в игры: <b>{games_current_profile}</b>'

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

        # Если профили закончились
        else:
            if language == '🇷🇺 Русский':
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

    # Если пользователь нажал 'zzz'
    elif symbol == '💤':
        # Если текущий язык пользователя Русский
        if language == '🇷🇺 Русский':
            await message.answer('Подождем, пока кто-то увидит твою анкету')
            await message.answer('1. Смотреть анкеты\n'
                                 '2. Моя анкета\n'
                                 '3. Я больше не хочу никого искать',
                                 reply_markup=ReplyKeyboardMarkup(keyboard=[
                                     [
                                         KeyboardButton(text='1 🔎'),
                                         KeyboardButton(text='2'),
                                         KeyboardButton(text='3'),
                                     ]
                                 ], resize_keyboard=True, one_time_keyboard=True))

        # Если текущий язык пользователя Английский
        else:
            await message.answer("Let's wait until someone sees your profile")
            await message.answer("1. View profiles\n"
                                 "2. My profile\n"
                                 "3. I don't want to look for anyone anymore",
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
        # Если текущий язык пользователя Русский
        if language == '🇷🇺 Русский':
            await message.answer('Не знаю такой символ')

        # Если текущий язык пользователя Английский
        else:
            await message.answer("I don't know such a symbol")
