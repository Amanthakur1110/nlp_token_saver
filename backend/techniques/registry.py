"""
registry.py – auto-discovers all technique.py files and registers them.

To add a new technique:
  1. Create techniques/my_technique/technique.py
  2. Define ONE class that extends BaseTechnique
  That is it. No other file needs to change.
"""
import importlib
import pkgutil
import pathlib
import inspect

from techniques.base import BaseTechnique

_registry: dict[str, BaseTechnique] = {}
_loaded = False


def _load_all():
    """Walk the techniques directory and import every technique.py."""
    global _loaded
    if _loaded:
        return
    _loaded = True

    techniques_dir = pathlib.Path(__file__).parent

    for folder in sorted(techniques_dir.iterdir()):
        if not folder.is_dir():
            continue
        module_file = folder / "technique.py"
        if not module_file.exists():
            continue

        # Build dotted module path: techniques.whitespace_cleanup.technique
        module_name = f"techniques.{folder.name}.technique"
        try:
            module = importlib.import_module(module_name)
        except Exception as e:
            print(f"[registry] Failed to import {module_name}: {e}")
            continue

        # Find the one class that extends BaseTechnique (but is not BaseTechnique itself)
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls, BaseTechnique) and cls is not BaseTechnique:
                instance = cls()
                _registry[instance.id] = instance
                break


def get_all_techniques() -> list[BaseTechnique]:
    _load_all()
    return list(_registry.values())


def get_technique_by_id(technique_id: str):
    _load_all()
    return _registry.get(technique_id)

