from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from guidance.models import Model

T = TypeVar("T")


class Parser(ABC, Generic[T]):
    @abstractmethod
    def create_prompt(self) -> Any:
        ...

    @abstractmethod
    def extract_answer(self, output: Model) -> T:
        ...
