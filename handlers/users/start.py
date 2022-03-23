from aiogram import types
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from keyboards.inline.gaming_keyboards import language_keyboard
from loader import db, dp, _


# Попадаем сюда, когда пользователь нажал /start или "Изменить анкету"
@dp.message_handler(filters.Text(startswith=['Изменить анкету', 'Edit profile']), state='check_profile')
@dp.message_handler(filters.Text(startswith=['Изменить анкету', 'Edit profile']), state='check_profile_just_play')
@dp.message_handler(CommandStart(), state='*')
async def bot_start(message: types.Message, state: FSMContext):
    await state.reset_state()
    await db.add_new_user()
    user_id = message.from_user.id
    await state.update_data(user_id=user_id)
    text = 'First of all I need to know which language do you speak? It’s will affect only on the menu language!\n\n' \
           'Прежде всего мне нужно знать, на каком языке вы говорите? Это повлияет только на язык меню!'
    await message.answer(text=_(text), reply_markup=language_keyboard)
    await state.set_state('vote_language')


# Узнаем язык пользователя
@dp.message_handler(state='vote_language')
async def get_user_language(message: types.Message, state: FSMContext):
    language = message.text
    await state.update_data(language=language)
    await db.set_language(language=language)

    text_ru = 'Данный бот создан энтузиастами, у нас нету многолетнего опыта в программирование и создание ботов - ' \
              'мы просто любим игры и хотели бы найти кого-то из наших городов. В боте никогда не придется платить, ' \
              'что бы увидеть кто вам поставил лайк и найти взаимную симпатию, все будет абсолютно бесплатно и ' \
              'ограничиваться только железом что бы не было спамеров, но за это будем у вас просить поддержать наши ' \
              '“возможных” будущих спонсоров и возможно будем держаться на донатах! ' \
              'На данный момент лучшей поддержкой для нас будет заказать буст у @boost_ace'

    text_en = "This bot was created by enthusiasts, we don't have many years of experience in programming and " \
              "creating bots - we just love games and would like to find someone from our cities. You will never " \
              "have to pay in the bot to see who gave you a like and find mutual sympathy, everything will be " \
              "absolutely free and limited only to hardware so that there are no spammers, but for this we will " \
              "ask you to support our 'possible' future sponsors and maybe we will keep on donates! At the moment, " \
              "the best support for us will be to order a boost from @boost_ace"

    if language == '🇷🇺 Русский':
        await message.answer(text=text_ru, reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text='Хорошо'
                    )
                ]
            ], resize_keyboard=True, one_time_keyboard=True))
    else:
        await message.answer(text=text_en, reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text='Good'
                    )
                ]
            ], resize_keyboard=True, one_time_keyboard=True))

    await state.set_state('choice_games')
