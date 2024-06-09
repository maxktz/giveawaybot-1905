import inspect  # noqa: F401
from abc import ABC, abstractmethod
from typing import Any, Callable

from .base import DEFAULT_NAMESPACE


class AbstractKeyBuilder(ABC):

    def __init__(
        self,
        func: Callable | str = None,
        namespace: str = DEFAULT_NAMESPACE,
    ) -> None:
        super().__init__()
        self.func = func
        self.namespace = namespace

    @abstractmethod
    def __call__(
        self,
        *args: tuple[Any, ...],
        func: Callable | str = None,
        **kwargs: dict[str, Any],
    ) -> str:
        """Build cache key for a function call with specific arguments"""


class KeyBuilder(AbstractKeyBuilder):

    def __call__(
        self,
        *args: tuple[Any, ...],
        func: Callable | str = None,
        **kwargs: dict[str, Any],
    ) -> str:
        func = func or self.func
        if func is None:
            raise ValueError('Not found argument "func" to build key for')

        if isinstance(func, Callable):
            # create key for function
            func_str = f"{func.__module__}:{func.__name__}"

            # map args to kwargs by getting function's key-word arguments (parameters)
            # params = inspect.signature(func).parameters
            # kwargs = kwargs | dict(zip(params, args))
            # # clear args because we have them in kwargs
            # args = ()
        else:
            func_str = str(func)

        # turn args and kwargs into a string
        args_str = ":".join(
            [str(arg) for arg in args] + [f"{key}={value}" for key, value in sorted(kwargs.items())]
        )

        # add namespace to the key
        key = f"{self.namespace}:{func_str}:{args_str}"

        return key
