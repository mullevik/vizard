from abc import ABC, abstractmethod

from pygame import Surface


class AbstractRenderer(ABC):
    """
    Abstract renderer used for rendering GameObjects onto a a PyGame surface
    """
    screen: Surface  # screen to render to

    @abstractmethod
    def render(self, surface: Surface) -> None:
        """Draw frames onto the given surface."""
        raise NotImplementedError
