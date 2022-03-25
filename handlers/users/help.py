from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp, _


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = _(("Список команд: ",
              "/start - Начать диалог",
              "/help - Получить справку"))

    await message.answer("\n".join(text))
