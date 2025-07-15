from utils import settings
from utils import logger
import asyncio


async def purchase_gifts(bot_client, tg_client, gifts_to_buy):
    bought_count = 0
    total_attempts = 0
    error_messages = []

    star_balance_before = await tg_client.get_stars_balance()

    for gift_info in gifts_to_buy:
        gift_id = gift_info['gift_id']
        available = gift_info['available_amount']

        for attempt in range(1, settings.GIFT_BUY + 1):
            if available <= 0:
                logger.warning(f"Больше нет доступных подарков с id {gift_id} для покупки.")
                break

            try:
                await tg_client.send_gift(
                    chat_id=settings.ID_BUY,
                    gift_id=gift_id,
                    text='Подарок куплен через @mallinmakin'
                )
                bought_count += 1
                total_attempts += 1
            except Exception as e:
                error_msg = f"Попытка {attempt} из {settings.GIFT_BUY} не удалось купить подарок {gift_id}: {e}"
                logger.error(error_msg)

                if len(error_messages) < 5:
                    error_messages.append(error_msg)

            # Каждые 5 попыток обновляем количество доступных подарков
            if attempt % 5 == 0:
                available = await _refresh_gift_availability(tg_client, gift_id)
                await asyncio.sleep(1)

    star_balance_after = await tg_client.get_stars_balance()

    errors_text = ""
    if error_messages:
        errors_text = "<b>Ошибки во время покупки (первые 5):</b>\n<blockquote expandable>" + "\n".join(error_messages) + "</blockquote>"

    summary_message = (
        f"<b>✅ Куплено {bought_count} подарков из {total_attempts} попыток.\n\n"
        f"⭐ Потрачено звёзд: {star_balance_before - star_balance_after}\n"
        f"⭐ Звёзд до покупки: {star_balance_before}\n"
        f"⭐ Звёзд после покупки: {star_balance_after}</b>\n\n"
        f"{errors_text}"
    )

    await bot_client.send_message(chat_id=settings.NOTIFICATION_ID, text=summary_message)

    return bought_count


async def _refresh_gift_availability(tg_client, gift_id):
    gifts = await tg_client.get_available_gifts()
    for gift in gifts:
        if gift.id == gift_id:
            return gift.available_amount
    return 0
