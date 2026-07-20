from abc import ABC, abstractmethod
from typing import Any


class Filter(ABC):
    """Pipes-and-Filters interface: transforms a shared context dict and passes it on."""

    @abstractmethod
    def process(self, context: dict[str, Any]) -> dict[str, Any]:
        ...


class Pipeline:
    """Chains filters, feeding each filter's output context into the next."""

    def __init__(self, filters: list[Filter]) -> None:
        self.filters = filters

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        for filter_ in self.filters:
            context = filter_.process(context)
        return context
