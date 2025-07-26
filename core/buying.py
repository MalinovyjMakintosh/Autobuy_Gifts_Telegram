from utils import settings
from utils.logger import logger as log
import asyncio
import json


# Загружаем список ID из gifts.json
def load_recorded_ids():
    try:
        with open("gifts.json", encoding="utf-8") as f:
            recorded = json.load(f)
            return {entry["id"] for entry in recorded}
    except Exception:
        return set()


async def purchase_gifts(bot_client, tg_client, gifts_to_buy):
    bought_count = 0
    total_attempts = 0
    error_messages = []

    recorded_ids = load_recorded_ids()
    warned_ids = set()

    star_balance_before = await tg_client.get_stars_balance()
    spent_per_profile = {name: 0 for name in settings.ACTIVE_PROFILES}
    purchased_ids = set()

    for profile in settings.ACTIVE_PROFILES:
        profile_settings = settings.PROFILES[profile]
        max_spend = profile_settings['MAX_TOTAL_SPEND']
        profile_gifts = [
            g for g in gifts_to_buy
            if g['gift_id'] not in purchased_ids and
               profile == g['profile']
        ]

        for gift_info in profile_gifts:
            gift_id = gift_info['gift_id']
            price = gift_info['price']
            available = gift_info['available_amount']

            if available <= 0:
                if gift_id not in recorded_ids and gift_id not in warned_ids:
                    log.warning(f"Нет доступных подарков {gift_id} для покупки.")
                    warned_ids.add(gift_id)
                continue

            if spent_per_profile[profile] + price > max_spend:
                log.info(f"⛔ Профиль {profile} достиг лимита ({spent_per_profile[profile]}/{max_spend}). Пропускаем {gift_id}")
                continue

            for attempt in range(1, settings.GIFT_BUY + 1):
                try:
                    await tg_client.send_gift(
                        chat_id=settings.ID_BUY,
                        gift_id=gift_id,
                        text=f'Подарок куплен через профиль {profile}'
                    )
                    bought_count += 1
                    total_attempts += 1
                    spent_per_profile[profile] += price
                    purchased_ids.add(gift_id)
                    log.success(f"✅ Куплен {gift_id} за {price}⭐ по профилю {profile}")
                    break
                except Exception as e:
                    error_msg = f"❌ Попытка {attempt} — ошибка при покупке {gift_id}: {e}"
                    log.error(error_msg)
                    if len(error_messages) < 5:
                        error_messages.append(error_msg)

                if attempt % 5 == 0:
                    available = await _refresh_gift_availability(tg_client, gift_id)
                    await asyncio.sleep(1)

    star_balance_after = await tg_client.get_stars_balance()

    errors_text = ""
    if error_messages:
        errors_text = "<b>Ошибки (первые 5):</b>\n<blockquote expandable>" + "\n".join(error_messages) + "</blockquote>"

    summary_lines = [
        f"<b>✅ Куплено {bought_count} подарков из {total_attempts} попыток</b>",
        f"⭐ Потрачено всего: {star_balance_before - star_balance_after}",
        f"⭐ До: {star_balance_before} | После: {star_balance_after}",
        "",
        f"<b>💼 Траты по профилям:</b>"
    ]
    for prof, spent in spent_per_profile.items():
        summary_lines.append(f"• {prof}: {spent} / {settings.PROFILES[prof]['MAX_TOTAL_SPEND']}")

    if errors_text:
        summary_lines.append("")
        summary_lines.append(errors_text)

    await bot_client.send_message(
        chat_id=settings.NOTIFICATION_ID,
        text="\n".join(summary_lines)
    )

    return bought_count


async def _refresh_gift_availability(tg_client, gift_id):
    gifts = await tg_client.get_available_gifts()
    for gift in gifts:
        if gift.id == gift_id:
            return gift.available_amount
    return 0
