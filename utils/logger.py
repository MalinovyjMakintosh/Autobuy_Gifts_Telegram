from loguru import logger
from .logging_setup import logging_setup

# Настроим логгер при импорте
logging_setup()

# Экспорт
__all__ = ["logger"]
