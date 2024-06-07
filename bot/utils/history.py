DEFAULT_HISTORY = ("menu",)


def update_history(history: tuple[str], new: str) -> tuple[str]:
    """Update callback_data history of user

    Add's new element in history if it is not exists history,
    otherwise slice history up to element.

    Args:
        history (tuple[str]): Ex history
        new (str): New element

    Returns:
        tuple[str]: New history
    """
    if new in history:
        # slice to the "new" element INCLUSIVE
        return history[: history.index(new) + 1]
    return (*history, new)


def back_callback_data(history: tuple[str]) -> str | None:
    try: 
        return history[-2]
    except IndexError:
        return None