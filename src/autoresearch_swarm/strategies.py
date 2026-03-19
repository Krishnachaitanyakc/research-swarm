"""Agent strategies for generating experiment modifications."""

import importlib
import os
import random
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type


class StrategyBase(ABC):
    """Abstract base class for all strategies."""

    @abstractmethod
    def generate(self, params: Dict[str, Any], best_known: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ...


class ExplorerStrategy(StrategyBase):
    """Random perturbations to parameters - broad search."""

    def generate(self, params: Dict[str, Any], best_known: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        new_params = {}
        for key, value in params.items():
            if isinstance(value, float):
                factor = random.uniform(0.1, 10.0)
                new_params[key] = value * factor
            elif isinstance(value, int):
                factor = random.uniform(0.25, 4.0)
                new_params[key] = max(1, int(value * factor))
            else:
                new_params[key] = value
        return new_params


class ExploiterStrategy(StrategyBase):
    """Refine the best known parameters with small perturbations."""

    def generate(self, params: Dict[str, Any], best_known: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        base = best_known if best_known is not None else params
        new_params = {}
        for key, value in base.items():
            if isinstance(value, float):
                factor = random.uniform(0.8, 1.2)
                new_params[key] = value * factor
            elif isinstance(value, int):
                delta = max(1, int(value * 0.2))
                new_params[key] = max(1, value + random.randint(-delta, delta))
            else:
                new_params[key] = value
        return new_params


class SpecialistStrategy(StrategyBase):
    """Focus on modifying a single hyperparameter."""

    def __init__(self, focus_param: Optional[str] = None):
        self.focus_param = focus_param

    def generate(self, params: Dict[str, Any], best_known: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        new_params = dict(params)
        numeric_keys = [k for k, v in params.items() if isinstance(v, (int, float))]
        if not numeric_keys:
            return new_params

        target = self.focus_param if self.focus_param and self.focus_param in params else random.choice(numeric_keys)
        value = params[target]
        if isinstance(value, float):
            new_params[target] = value * random.uniform(0.1, 10.0)
        elif isinstance(value, int):
            factor = random.uniform(0.25, 4.0)
            new_params[target] = max(1, int(value * factor))
        return new_params


def load_plugins(directory: str) -> Dict[str, Type[StrategyBase]]:
    """Discover strategy plugins from a directory.

    Each .py file in the directory is imported. Any class that is a subclass
    of StrategyBase (but not StrategyBase itself) is registered using a
    lowercased version of its class name (minus 'Strategy' suffix if present).
    """
    plugins: Dict[str, Type[StrategyBase]] = {}
    if not os.path.isdir(directory):
        return plugins
    sys.path.insert(0, directory)
    try:
        for fname in sorted(os.listdir(directory)):
            if not fname.endswith(".py") or fname.startswith("_"):
                continue
            module_name = fname[:-3]
            spec = importlib.util.spec_from_file_location(
                module_name, os.path.join(directory, fname)
            )
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, StrategyBase)
                    and attr is not StrategyBase
                ):
                    name = attr_name.lower()
                    if name.endswith("strategy"):
                        name = name[: -len("strategy")]
                    plugins[name] = attr
    finally:
        sys.path.pop(0)
    return plugins
