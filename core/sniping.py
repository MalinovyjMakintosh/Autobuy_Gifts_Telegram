import json
from utils import settings
from utils import logger


async def fetch_new_gifts(bot_client, tg_client):
    available_gifts = await tg_client.get_available_gifts()

    try:
        with open('gifts.json', encoding='utf-8') as f:
            recorded_gifts = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        recorded_gifts = []

    gifts_to_purchase = []

    for gift in available_gifts:
        current_gift = {'id': gift.id, 'price': gift.price}

        if current_gift not in recorded_gifts:
            recorded_gifts.append(current_gift)
            with open('gifts.json', 'w', encoding='utf-8') as f:
                json.dump(recorded_gifts, f, ensure_ascii=False, indent=2)

            if settings.SEND_NOTIFICATIONS:
                status = f'Ограничено ({gift.available_amount})' if gift.is_limited else 'Без ограничений'

                try:
                    sticker = await bot_client.download_media(gift.sticker.file_id, in_memory=True)
                    sticker.name = 'sticker.tgs'
                    await bot_client.send_sticker(chat_id=settings.NOTIFICATIONS_ID, sticker=sticker)
                except Exception as err:
                    logger.error(f"Не удалось отправить стикер в {settings.NOTIFICATIONS_ID}: {err}")

                try:
                    message = (
                        f'<b>🧨 НОВЫЙ ПОДАРОК 🧨\n'
                        f'❗️ {status}\n\n'
                        f'⭐ Цена: {gift.price} STAR\n'
                        f'🎁 Количество: {gift.total_amount}</b>'
                    )
                    await bot_client.send_message(chat_id=settings.NOTIFICATIONS_ID, text=message)
                except Exception as err:
                    logger.error(f"Не удалось отправить сообщение о подарке в {settings.NOTIFICATIONS_ID}: {err}")

            if not gift.is_limited:
                continue

            if not (settings.SUPPLY_LIMIT["FROM"] < gift.total_amount < settings.SUPPLY_LIMIT["TO"]):
                continue

            if not (settings.PRICE_LIMIT['FROM'] < gift.price < settings.PRICE_LIMIT['TO']):
                continue

            if settings.GIFT_BUY:
                gifts_to_purchase.append({
                    'gift_id': gift.id,
                    'available_amount': gift.available_amount
                })

    return gifts_to_purchase
