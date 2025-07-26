import sys
from loguru import logger


def formatter(record, format_string):
    return format_string + record["extra"].get("end", "\n") + "{exception}"


def logging_setup():
    format_info = "<green>{time:HH:mm:ss.SS}</green> | <blue>{level}</blue> | <level>{message}</level>"
    format_file = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {name}:{function}:{line} | {message}"

    logger.remove()

    logger.add(
        "logs/out.log",
        colorize=False,
        level="DEBUG",
        encoding="utf-8",
        format=lambda record: formatter(record, format_file),
        rotation="10 MB",
        retention="7 days"
    )

    logger.add(
        sys.stdout,
        colorize=True,
        level="INFO",
        format=lambda record: formatter(record, format_info)
    )
