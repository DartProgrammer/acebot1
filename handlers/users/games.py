from aiogram import types
from aiogram.dispatcher import FSMContext, filters
from aiogram.types import ReplyKeyboardRemove

from keyboards.inline.gaming_keyboards import show_games_keyboard
from loader import dp


# Сюда попадаем, когда просим пользователя выбрать игры, в которые он играет
@dp.message_handler(state='choice_games')
async def choice_games(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language')
    text_ru = 'Выбери игру (игры), в которые вы играете! После нажатия на одну игру, вы сможете добавить еще одну.'
    text_en = 'Choose the game(s) you are playing! After clicking on one game, you will be able to add another one.'

    if language == '🇷🇺 Русский':
        await message.answer(text=text_ru, reply_markup=show_games_keyboard(language))
    else:
        await message.answer(text=text_en, reply_markup=show_games_keyboard(language))

    await state.set_state('choice_games_more')


# Сюда попадаем, когда пользователь выбрал игру "PUBG MOBILE"
@dp.message_handler(text='PUBG MOBILE', state='choice_games_more')
async def choice_games1(message: types.Message, state: FSMContext):
    game1 = message.text
    data = await state.get_data()
    language = data.get('language')
    game2 = data.get('game2')
    await state.update_data(game1=game1)

    if game2 is None:
        text_ru = f'Вы играете в игру <b>{game1}</b>, хотите ли вы добавить еще какую-то игру или будем искать ' \
                  f'людей только в этой игре?'
        text_en = f'You are playing the <b>{game1}</b>, do you want to add another game or will we look for people ' \
                  f'only in this game?'
    else:
        text_ru = f'Вы играете в игры <b>{game1}, {game2}</b>, нажмите "Продолжить"'
        text_en = f'You are playing games <b>{game1}, {game2}</b>, click "Continue"'

    if language == '🇷🇺 Русский':
        await message.answer(text=text_ru, reply_markup=show_games_keyboard(language, game1, game2))
    else:
        await message.answer(text=text_en, reply_markup=show_games_keyboard(language, game1, game2))


# Сюда попадаем, когда пользователь выбрал игру "PUBG New State"
@dp.message_handler(text='PUBG New State', state='choice_games_more')
async def choice_games2(message: types.Message, state: FSMContext):
    game2 = message.text
    data = await state.get_data()
    language = data.get('language')
    game1 = data.get('game1')
    await state.update_data(game2=game2)

    if game1 is None:
        text_ru = f'Вы играете в игру <b>{game2}</b>, хотите ли вы добавить еще какую-то игру или будем искать ' \
                  f'людей только в этой игре?'
        text_en = f'You are playing the <b>{game2}</b>, do you want to add another game or will we look for people ' \
                  f'only in this game?'
    else:
        text_ru = f'Вы играете в игры <b>{game1}, {game2}</b>, нажмите "Продолжить"'
        text_en = f'You are playing games <b>{game1}, {game2}</b>, click "Continue"'

    if language == '🇷🇺 Русский':
        await message.answer(text=text_ru, reply_markup=show_games_keyboard(language, game2, game1))
    else:
        await message.answer(text=text_en, reply_markup=show_games_keyboard(language, game2, game1))


# Сюда попадаем, когда пользователь нажал "Продолжить". Узнаем возраст пользователя
@dp.message_handler(filters.Text(startswith=['Продолжить', 'Continue'], ignore_case=True), state='choice_games_more')
async def enter_age(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language')
    text_ru = 'Сколько тебе лет?'
    text_en = 'How old are you?'

    if language == '🇷🇺 Русский':
        await message.answer(text=text_ru, reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(text=text_en, reply_markup=ReplyKeyboardRemove())

    await state.set_state('age')
