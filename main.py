import asyncio
import random
from utils.logger import logger
from utils import settings
from core.sniping import fetch_new_gifts
from core.buying import purchase_gifts
from pyrogram import Client 


async def create_clients():
    # Инициализация клиента бота
    bot = Client('TgBot', bot_token=settings.BOT_TOKEN, api_id=settings.API_ID, api_hash=settings.API_HASH)
    await bot.start()
    bot_info = await bot.get_me()
    bot_full_name = f"{bot_info.first_name} {bot_info.last_name or ''}".strip()
    logger.info(f"Клиент бота запущен: {bot_full_name} (@{bot_info.username}), ID: {bot_info.id}")

    # Инициализация аккаунта для покупки подарков
    user_account = Client('TgAccount', api_id=settings.API_ID, api_hash=settings.API_HASH)
    if settings.GIFT_BUY:
        await user_account.start()
        user_info = await user_account.get_me()

        try:
            await user_account.resolve_peer(settings.ID_BUY)
        except Exception as error:
            logger.critical(f"Указан неверный ID_BUY: {error}")
            exit(1)

        user_full_name = f"{user_info.first_name} {user_info.last_name or ''}".strip()

        # Получаем количество звезд у пользователя
        try:
            user_stars = await user_account.get_stars_balance(chat_id="me")
        except Exception as e:
            user_stars = "N/A"
            logger.error(f"Не удалось получить баланс звезд пользователя: {e}")

        logger.info(
            f"✨ Клиент аккаунта запущен:\n"
            f"👤 Пользователь: {user_full_name} (@{user_info.username})\n"
            f"🆔 ID: {user_info.id}\n"
            f"🌟 Баланс звёзд: {user_stars}\n"
            f"🛒 Чат для покупки ID: {settings.ID_BUY}"
        )

    else:
        logger.info("Покупка подарков отключена, инициализация аккаунта пропущена.")

    return bot, user_account


async def run_bot():
    bot_client, user_client = await create_clients()
    logger.info("Ожидание появления новых подарков...")

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
            logger.error(f"Неожиданная ошибка в основном цикле: {exc}")
            await asyncio.sleep(1)


if __name__ == "__main__":
    print("Софт от паблика - https://t.me/mallinmakin")
    asyncio.run(run_bot())
