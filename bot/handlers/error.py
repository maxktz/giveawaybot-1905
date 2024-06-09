from aiogram import Router
from aiogram.types import ErrorEvent
from loguru import logger

# from aiogram.exceptions import TelegramBadRequest

router = Router(name="errors")


@router.error()
async def log_uncatched_exceptions(error: ErrorEvent):
    logger.exception(error.exception)
