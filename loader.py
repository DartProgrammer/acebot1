from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data import config
from middlewares.throttling import ThrottlingMiddleware
from utils.db_api.db_commands import DBCommands
from middlewares.language import LanguageMiddleware

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db = DBCommands()
i18n = LanguageMiddleware(config.I18N_DOMAIN, config.LOCALES_PATH)

dp.middleware.setup(ThrottlingMiddleware())
dp.middleware.setup(i18n)

_ = i18n.gettext
