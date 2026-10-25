"""
base.py – BaseTechnique abstract class.

Every technique extends this. The registry finds technique.py files,
imports them, and looks for the class that extends BaseTechnique.
"""
from abc import ABC, abstractmethod


class BaseTechnique(ABC):
    # Subclasses set these as class attributes
    id: str = ""
    name: str = ""
    description: str = ""

    # params_schema tells the frontend what controls to render.
    # Each entry: {name, type, label, default, min?, max?, options?}
    params_schema: list = []

    @abstractmethod
    def apply(self, text: str, params: dict) -> str:
        """Apply the technique to text and return the compressed version."""

    def is_available(self) -> tuple[bool, str]:
        """
        Return (True, "") if the technique can run,
        or (False, "reason") if a dependency is missing.
        Default: always available.
        """
        return True, ""

