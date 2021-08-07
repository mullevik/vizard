from abc import ABC, abstractmethod
from typing import Any


class AbstractAction(ABC):

    @abstractmethod
    def apply(self, subject: Any):
        raise NotImplementedError


class ActionException(Exception):
    """
    Actions are expected to throw this exception
    if something invalid happens
    """
    pass
