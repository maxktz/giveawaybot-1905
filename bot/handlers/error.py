from aiogram import Router
from aiogram.types import ErrorEvent
from loguru import logger
from aiogram.exceptions import TelegramBadRequest

router = Router(name="errors")


@router.error()
async def log_uncatched_exceptions(error: ErrorEvent):
    if type(error.exception) is TelegramBadRequest:
        e: TelegramBadRequest = error.exception
        if (
            e.message
            == "Bad Request: query is too old and response timeout expired or query ID is invalid"
        ):
            return

    logger.exception(error.exception)
