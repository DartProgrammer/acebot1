from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from keyboards.inline.gaming_keyboards import profile_action_target_keyboard, menu_my_profile_keyboard
from loader import dp, db, _
from utils.db_api import models
from keyboards.inline.gaming_keyboards import ru_button


# Сюда попадаем, когда пользователь нажал "zzz"
@dp.message_handler(state='zzz_second_user')
async def handler_zzz(message: types.Message, state: FSMContext):
    second_user_id = message.from_user.id
    second_user: models.User = await db.get_user(second_user_id)
    option = message.text

    # Если пользователь выбрал вариант 1 "Показать профили, которым я нравлюсь"
    if option == '1':
        # Получаем всех пользователей, которые лайкнули анкету
        all_users_liked = await db.get_users_liked_my_profile(second_user_id)
        current_profile_liked_number = 0
        count_users_liked = len(all_users_liked)
        current_profile: models.User = all_users_liked[current_profile_liked_number]
        count_users_liked_for_text = count_users_liked - 1

        await state.update_data(second_user=second_user,
                                all_users_liked=all_users_liked,
                                count_users_liked=count_users_liked,
                                current_profile_liked_number=current_profile_liked_number,
                                count_users_liked_for_text=count_users_liked_for_text)

        photo = current_profile.photo
        game1 = current_profile.game1
        game2 = current_profile.game2

        if game1 is not None and game2 is not None:
            games = f'{game1}, {game2}'
        elif game2 is None:
            games = f'{game1}'
        elif game1 is None:
            games = f'{game2}'
        else:
            games = ''

        if count_users_liked == 1:
            text = _('Кому-то понравилась твоя анкета:\n\n'
                     '{current_profile.name}, {current_profile.age} из {current_profile.country}\n'
                     'Хобби: <b>{current_profile.hobby}</b>\n'
                     'О себе: <b>{current_profile.about_yourself}</b>\n'
                     'Играет в игры: <b>{games}</b>').format(current_profile=current_profile, games=games)
        else:
            text = _('Кому-то понравилась твоя анкета (и ещё {count_users_liked_for_text})\n\n'
                     '{current_profile.name}, {current_profile.age} из {current_profile.country}\n'
                     'Хобби: <b>{current_profile.hobby}</b>\n'
                     'О себе: <b>{current_profile.about_yourself}</b>\n'
                     'Играет в игры: <b>{games}</b>').format(count_users_liked_for_text=count_users_liked_for_text,
                                                             current_profile=current_profile, games=games)

        # Если пользователь без фото
        if photo == 'None':
            await message.answer(text=text, reply_markup=profile_action_target_keyboard)

        # Если пользователь с фото
        else:
            await message.answer_photo(photo=photo, caption=text, reply_markup=profile_action_target_keyboard)

        await state.set_state('in_like')

    # Если пользователь выбрал вариант 2 "Моя анкета"
    elif option == '2':

        game1 = second_user.game1
        game2 = second_user.game2

        if game1 is not None and game2 is not None:
            games = f'{game1}, {game2}'
        elif game2 is None:
            games = f'{game1}'
        elif game1 is None:
            games = f'{game2}'
        else:
            games = ''

        text_ru = _('Имя: <b>{second_user.name}</b>\n'
                    'Возраст: <b>{second_user.age}</b>\n'
                    'Пол: <b>{second_user.gender}</b>\n'
                    'Ищу: <b>{second_user.purpose}</b>\n'
                    'Кого ищу: <b>{second_user.who_search}</b>\n'
                    'Страна: <b>{second_user.country}</b>\n'
                    'Город: <b>{second_user.city}</b>\n'
                    'О себе: <b>{second_user.about_yourself}</b>\n'
                    'Хобби: <b>{second_user.hobby}</b>\n'
                    'В какие игры играю: <b>{games}</b>').format(second_user=second_user, games=games)

        await message.answer(_('Ваш профиль:'))

        if second_user.photo == 'None':
            await message.answer(text=text_ru)
        else:
            await message.answer_photo(photo=second_user.photo, caption=text_ru)

        await message.answer(text=_('1. Заполнить анкету заново\n'
                                    '2. Изменить фото\n'
                                    '3. Изменить текст анкеты\n'
                                    '4. Смотреть анкеты'), reply_markup=menu_my_profile_keyboard)

        await state.update_data(user_=second_user)
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

        await state.set_state('disable_second_profile')

    # Если пользователь не выбрал вариант, а что-то написал
    else:
        await message.answer(_('Нет такого варианта ответа'))


# Сюда попадаем, когда пользователь нажал "zzz"
@dp.message_handler(state='zzz_second_user_send_message')
async def handler_zzz(message: types.Message, state: FSMContext):
    second_user_id = message.from_user.id
    second_user: models.User = await db.get_user(second_user_id)
    language_second_user = second_user.language
    option = message.text

    # Если пользователь выбрал вариант 1 "Показать профили, которым я нравлюсь"
    if option == '1':

        # Получаем всех пользователей, которые написали письмо
        all_users_send_message = await db.get_users_send_message(second_user_id)
        current_profile_send_message = 0
        count_users_send_message = len(all_users_send_message)
        current_profile: models.User = all_users_send_message[current_profile_send_message]
        count_users_send_message_for_text = count_users_send_message - 1

        await state.update_data(second_user=second_user,
                                all_users_send_message=all_users_send_message,
                                count_users_send_message=count_users_send_message,
                                current_profile_send_message=current_profile_send_message,
                                count_users_send_message_for_text=count_users_send_message_for_text)

        photo = current_profile.photo
        game1 = current_profile.game1
        game2 = current_profile.game2

        if game1 is not None and game2 is not None:
            games = f'{game1}, {game2}'
        elif game2 is None:
            games = f'{game1}'
        elif game1 is None:
            games = f'{game2}'
        else:
            games = ''

        if count_users_send_message == 1:
            text = _('Кому-то понравилась твоя анкета:\n\n'
                     '{current_profile.name}, {current_profile.age} из {current_profile.country}\n'
                     'Хобби: <b>{current_profile.hobby}</b>\n'
                     'О себе: <b>{current_profile.about_yourself}</b>\n'
                     'Играет в игры: <b>{games}</b>'
                     'Письмо: <b>{current_profile.send_message_text}</b>').format(current_profile=current_profile,
                                                                                  games=games)
        else:
            text = _('Кому-то понравилась твоя анкета (и ещё {count_users_send_message_for_text})\n\n'
                     '{current_profile.name}, {current_profile.age} из {current_profile.country}\n'
                     'Хобби: <b>{current_profile.hobby}</b>\n'
                     'О себе: <b>{current_profile.about_yourself}</b>\n'
                     'Играет в игры: <b>{games}</b>'
                     'Письмо: <b>{current_profile.send_message_text}</b>').format(
                count_users_send_message_for_text=count_users_send_message_for_text, current_profile=current_profile,
                games=games)

        # Если пользователь без фото
        if photo == 'None':
            await message.answer(text=text, reply_markup=profile_action_target_keyboard)

        # Если пользователь с фото
        else:
            await message.answer_photo(photo=photo, caption=text, reply_markup=profile_action_target_keyboard)

        await state.set_state('in_send_message')

    # Если пользователь выбрал вариант 2 "Моя анкета"
    elif option == '2':
        game1 = second_user.game1
        game2 = second_user.game2

        if game1 is not None and game2 is not None:
            games = f'{game1}, {game2}'
        elif game2 is None:
            games = f'{game1}'
        elif game1 is None:
            games = f'{game2}'
        else:
            games = ''

        # Если текущий язык пользователя Русский
        if language_second_user == ru_button.text:
            text = _('Имя: <b>{second_user.name}</b>\n'
                     'Возраст: <b>{second_user.age}</b>\n'
                     'Пол: <b>{second_user.gender}</b>\n'
                     'Ищу: <b>{second_user.purpose}</b>\n'
                     'Кого ищу: <b>{second_user.who_search}</b>\n'
                     'Страна: <b>{second_user.country}</b>\n'
                     'Город: <b>{second_user.city}</b>\n'
                     'О себе: <b>{second_user.about_yourself}</b>\n'
                     'Хобби: <b>{second_user.hobby}</b>\n'
                     'В какие игры играю: <b>{games}</b>')

            await message.answer(_('Ваш профиль:'))

            if second_user.photo == 'None':
                await message.answer(text=text)
            else:
                await message.answer_photo(photo=second_user.photo, caption=text)

            await message.answer(text=_('1. Заполнить анкету заново\n'
                                        '2. Изменить фото\n'
                                        '3. Изменить текст анкеты\n'
                                        '4. Смотреть анкеты'), reply_markup=menu_my_profile_keyboard)

        await state.update_data(user_=second_user)
        await state.set_state('my_profile_state')

    # Если пользователь выбрал вариант 3 "Я больше не хочу никого искать"
    elif option == '3':
        # Если текущий язык пользователя Русский
        if language_second_user == ru_button.text:
            text_ru = _('Так ты не узнаешь, что кому-то нравишься... Точно хочешь отключить свою анкету?\n\n'
                        '1. Да, отключить анкету.\n'
                        '2. Нет, вернуться назад.')

            await message.answer(text=text_ru, reply_markup=ReplyKeyboardMarkup(keyboard=[
                [
                    KeyboardButton(text='1'),
                    KeyboardButton(text='2')
                ]
            ], resize_keyboard=True, one_time_keyboard=True))

        await state.set_state('disable_second_profile')

    # Если пользователь не выбрал вариант, а что-то написал
    else:
        await message.answer(_('Нет такого варианта ответа'))
