from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from .menu import send_menu

router = Router(name="start")


@router.message(F.text.regexp(r"^/start(?:\s+\w+)?"))
async def start_handler(
    message: Message, session: AsyncSession, bot: Bot, state: FSMContext
) -> None:
    await state.set_state()
    await send_menu(user_id=message.from_user.id, session=session, bot=bot, state=state)
