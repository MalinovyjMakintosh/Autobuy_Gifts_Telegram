import asyncio
import random
import sys
import aiohttp
from utils.logger import logger as log
from utils import settings
from core.sniping import fetch_new_gifts
from core.buying import purchase_gifts
from pyrogram import Client


# Устанавливаем активные профили из аргументов (если переданы)
if len(sys.argv) > 1:
    cli_profiles = sys.argv[1:]
    settings.ACTIVE_PROFILES = [
        p for p in cli_profiles if p in settings.PROFILES
    ]
    log.info(f"🔧 Профили выбраны из аргументов запуска: {', '.join(settings.ACTIVE_PROFILES)}")

else:
    log.info(f"📦 Используются профили по умолчанию: {', '.join(settings.ACTIVE_PROFILES)}")



async def fetch_ip():
    try:
        proxy = settings.PROXY if settings.USE_PROXY else None

        connector = None
        if proxy:
            import aiohttp_socks
            proxy_url = f"{proxy['scheme']}://"
            if proxy['username'] and proxy['password']:
                proxy_url += f"{proxy['username']}:{proxy['password']}@"
            proxy_url += f"{proxy['hostname']}:{proxy['port']}"
            connector = aiohttp_socks.ProxyConnector.from_url(proxy_url)

        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get("https://api.ipify.org") as resp:
                ip = await resp.text()
                log.info(f"🌍 IP через прокси: {ip}")
    except Exception as e:
        log.warning(f"⚠️ Не удалось получить IP-адрес через прокси: {e}")


async def create_clients():
    await fetch_ip()
    proxy = settings.PROXY if settings.USE_PROXY else None

    # Бот
    bot = Client(
        'TgBot',
        bot_token=settings.BOT_TOKEN,
        api_id=settings.API_ID,
        api_hash=settings.API_HASH,
        proxy=proxy
    )
    await bot.start()
    bot_info = await bot.get_me()
    bot_full_name = f"{bot_info.first_name} {bot_info.last_name or ''}".strip()
    log.info(f"Клиент бота запущен: {bot_full_name} (@{bot_info.username}), ID: {bot_info.id}")

    # Пользователь
    user_account = Client(
        'TgAccount',
        api_id=settings.API_ID,
        api_hash=settings.API_HASH,
        proxy=proxy
    )
    if settings.GIFT_BUY:
        await user_account.start()
        user_info = await user_account.get_me()

        try:
            await user_account.resolve_peer(settings.ID_BUY)
        except Exception as error:
            log.critical(f"Указан неверный ID_BUY: {error}")
            exit(1)

        user_full_name = f"{user_info.first_name} {user_info.last_name or ''}".strip()

        try:
            user_stars = await user_account.get_stars_balance(chat_id="me")
        except Exception as e:
            user_stars = "N/A"
            log.error(f"Не удалось получить баланс звёзд пользователя: {e}")

        log.info(
            f"✨ Клиент аккаунта запущен:\n"
            f"👤 Пользователь: {user_full_name} (@{user_info.username})\n"
            f"🆔 ID: {user_info.id}\n"
            f"🌟 Баланс звёзд: {user_stars}\n"
            f"🛒 Чат для покупки ID: {settings.ID_BUY}"
        )
    else:
        log.info("Покупка подарков отключена, инициализация аккаунта пропущена.")

    return bot, user_account


async def run_bot():
    bot_client, user_client = await create_clients()
    log.info("Ожидание появления новых подарков...")

    while True:
        try:
            new_gifts = await fetch_new_gifts(bot_client, user_client)

            if settings.GIFT_BUY and new_gifts:
                await purchase_gifts(
                    bot_client=bot_client,
                    tg_client=user_client,
                    gifts_to_buy=new_gifts
                )

            sleep_time = random.uniform(5, 10)
            await asyncio.sleep(sleep_time)

        except Exception as exc:
            log.error(f"Неожиданная ошибка в основном цикле: {exc}")
            await asyncio.sleep(1)


if __name__ == "__main__":
    print("Софт от паблика - https://t.me/mallinmakin")
    asyncio.run(run_bot())
