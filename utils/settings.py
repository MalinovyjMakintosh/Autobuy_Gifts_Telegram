# Токен из https://my.telegram.org/
API_ID = 11111
API_HASH = 'Aaaaa'

# Токен бота от @BotFather
BOT_TOKEN = '11111:aaaa'

# ID аккаунта, которому бот будет писать о покупке подарков.
# Перед запуском программы нужно сначала написать этому боту
NOTIFICATIONS_ID = 22222
SEND_NOTIFICATIONS = True

# ID пользователя/канала, которому будут покупаться подарки
ID_BUY = 22222

# Количество подарков 
GIFT_BUY = 1

# Активные профили (в порядке приоритета)
ACTIVE_PROFILES = ["default", "default1"]

# Профили с индивидуальными лимитами
PROFILES = {
    "default": {
        "MAX_TOTAL_SPEND": 100,
        "PRICE_LIMIT": {"FROM": 0, "TO": 50},
        "SUPPLY_LIMIT": {"FROM": 1, "TO": 10000}
    },
    "default1": {
        "MAX_TOTAL_SPEND": 200,
        "PRICE_LIMIT": {"FROM": 50, "TO": 100},
        "SUPPLY_LIMIT": {"FROM": 10, "TO": 5000}
    }
}

# --- Прокси настройки ---
USE_PROXY = True
PROXY = {
    "scheme": "socks5",
    "hostname": "",
    "port": 11111,
    "username": "",
    "password": ""
}
