from environs import Env
from pathlib import Path

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение типа str
ADMINS_IDS = env.list("ADMINS")  # Тут у нас будет список из админов
IP = env.str("ip")  # Тоже str, но для айпи адреса хоста

# Параметры подключения к БД Postgres
PG_USER = env.str('PG_USER')
PG_PASS = env.str('PG_PASS')
DB_HOST = env.str('DB_HOST')
DB_NAME = env.str('DB_NAME')

BASE_DIR = Path(__file__).parent.parent
LOCALES_PATH = BASE_DIR / 'locales'
I18N_DOMAIN = 'acebot'

# Project constants
HOBBY_STRING_LENGTH = 40
