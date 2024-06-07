import functools
from typing import Optional, TypeVar

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _

F = TypeVar("F")


def append_navigation_row(
    buttons: list[list[InlineKeyboardButton]],
    back_callback_data: Optional[str] = None,
    back_to_menu: bool | None = None,
) -> None:
    if back_callback_data or back_to_menu is not False:
        back_navigate_row = []
        if back_callback_data:
            back_navigate_row.append(
                InlineKeyboardButton(text=_("back button"), callback_data=back_callback_data)
            )
        if back_to_menu is not False and back_callback_data != "menu":
            back_navigate_row.append(
                InlineKeyboardButton(text=_("back_to_menu button"), callback_data="menu")
            )
        buttons.append(back_navigate_row)


def with_navigation_row(func: F) -> F:
    """
    Wrapper that adds a navigation row to the InlineKeyboardMarkup returned by the function.

    Modified function will get 2 more parameters
        :back_callback_data: Optional[str] = None
        :back_to_menu: bool | None = None stands for auto-configuration

    :param func: A function that returns an InlineKeyboardMarkup.
    :return: A function that wraps the original function and adds a navigation row.
    """

    @functools.wraps(func)
    def wrapper(
        *args,
        back_callback_data: Optional[str] = None,
        back_to_menu: bool | None = None,
        **kwargs,
    ) -> InlineKeyboardMarkup:
        inline_markup: InlineKeyboardMarkup = func(*args, **kwargs)
        append_navigation_row(inline_markup.inline_keyboard, back_callback_data, back_to_menu)
        return inline_markup

    return wrapper
