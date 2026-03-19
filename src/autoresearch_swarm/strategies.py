"""Agent strategies for generating experiment modifications."""

import random
from typing import Any, Dict, Optional


class ExplorerStrategy:
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


class ExploiterStrategy:
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


class SpecialistStrategy:
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
