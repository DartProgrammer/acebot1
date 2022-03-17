from aiogram import types
from emoji import emojize


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand('my_profile', f'{emojize(":bust_in_silhouette:")} Моя анкета'),
            types.BotCommand('change_match', f'{emojize(":hammer_and_wrench:")} Изменить категорию поиска'),
            types.BotCommand('complain', f'{emojize(":prohibited:")} Пожаловаться'),
            types.BotCommand('language', f'{emojize(":globe_showing_Europe-Africa:")} Язык'),
            types.BotCommand('start', f'{emojize(":electric_plug:")} Перезапустить бота'),
        ]
    )
