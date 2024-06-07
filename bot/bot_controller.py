from aiogram import Bot
from aiogram.types import (
    ForceReply,
    InlineKeyboardMarkup,
    InputFile,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.types.base import UNSET_DISABLE_WEB_PAGE_PREVIEW, UNSET_PARSE_MODE


async def try_delete_message(bot: Bot, chat_id: int, message_id: int):
    if isinstance(chat_id, int) and isinstance(message_id, int):
        try:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception:
            return False
    return True


async def send_message(
    bot: Bot,
    chat_id: int,
    text: str,
    photo: InputFile | str = None,
    document: InputFile | str = None,
    parse_mode: str = UNSET_PARSE_MODE,
    reply_markup: (
        InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | list
    ) = None,
    disable_web_page_preview: bool = UNSET_DISABLE_WEB_PAGE_PREVIEW,
) -> Message:
    base_args = dict(
        chat_id=chat_id,
        parse_mode=parse_mode,
        reply_markup=reply_markup,
    )
    if isinstance(reply_markup, list):
        reply_markup = InlineKeyboardMarkup(inline_keyboard=reply_markup)
    if photo:
        return await bot.send_photo(
            **base_args,
            photo=photo,
            caption=text,
        )
    elif document:
        return await bot.send_document(
            **base_args,
            document=document,
            caption=text,
        )
    else:
        return await bot.send_message(
            **base_args,
            text=text,
            disable_web_page_preview=disable_web_page_preview,
        )
