import io
import random
from aiogram.types import BufferedInputFile, Message
from aiogram import Router, Bot
from aiogram.utils.i18n import gettext as _
from aiogram.fsm.context import FSMContext
from cachetools import TTLCache
from bot.bot_controller import try_delete_message
from sqlalchemy.ext.asyncio import AsyncSession
from captcha.image import ImageCaptcha
from aiogram.fsm.state import StatesGroup, State

from bot.services.users import set_is_verified

router = Router()


CAPTCHA_LENGTH = 5
image_captcha = ImageCaptcha(
    width=240,
    height=90,
)
_cached_captcha_texts: dict[int, str] = TTLCache(maxsize=10_000, ttl=24 * 60 * 60)


class States(StatesGroup):
    solve_captcha_state = State("solve_captcha_state")


async def send_captcha(
    bot: Bot,
    user_id: int,
    state: FSMContext,
    retried: bool = False,
) -> None:
    if retried:
        text = _("The goal has not been accomplished yet, please try again.")
    else:
        text = _("<b>Meet</b> captcha:")

    captcha_text = _cached_captcha_texts.get(user_id)
    if captcha_text is None:
        captcha_text = _gen_captcha_text()
    _cached_captcha_texts[user_id] = captcha_text
    captcha_image = _gen_captcha_image(captcha_text)

    tempdata = await state.get_data()
    await try_delete_message(bot, user_id, tempdata.get("ex_message_id"))
    msg = await bot.send_photo(
        chat_id=user_id,
        photo=captcha_image,
        caption=text,
    )
    await state.set_state(States.solve_captcha_state)
    await state.update_data({"ex_message_id": msg.message_id})


@router.message(States.solve_captcha_state)
async def handle_captcha(
    message: Message, session: AsyncSession, bot: Bot, state: FSMContext
) -> None:
    from .menu import send_menu

    await state.set_state()

    user = message.from_user
    captcha_text = _cached_captcha_texts.get(user.id)
    if captcha_text and _validate_captcha_response(captcha_text, message.text):
        _cached_captcha_texts.pop(user.id)
        await set_is_verified(session, user.id, True)
        return await send_menu(bot=bot, session=session, user_id=user.id, state=state)
    _cached_captcha_texts[user.id] = _gen_captcha_text()
    await send_captcha(bot=bot, user_id=user.id, state=state, retried=True)


def _gen_captcha_image(text: str) -> BufferedInputFile:
    byte_io = io.BytesIO()
    image_captcha.generate_image(text).save(byte_io, format="jpeg")
    byte_io.seek(0)
    return BufferedInputFile(byte_io.read(), "captcha.jpeg")


def _gen_captcha_text() -> str:
    symbols = "QWERTYUIPASDFGHJKLZXCVBNM2345689"
    return "".join(random.choice(symbols) for _ in range(CAPTCHA_LENGTH))


def _validate_captcha_response(captcha: str, captcha2: str) -> bool:
    return captcha.upper() == captcha2.upper()
