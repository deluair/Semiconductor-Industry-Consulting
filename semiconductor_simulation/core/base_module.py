from abc import ABC, abstractmethod
from typing import Dict, List, Any
from semiconductor_simulation.core.base_model import BaseModel

class BaseModule(ABC):
    """
    Abstract base class for all simulation modules.
    Each module encapsulates a specific part of the simulation logic.
    """
    def __init__(self, module_id: str, name: str):
        self.module_id = module_id
        self.name = name

    @abstractmethod
    def initialize(self, models: Dict[str, List[BaseModel]], global_params: Dict[str, Any]):
        """
        Initialize the module with relevant models and global simulation parameters.
        'models' could be a dictionary categorizing models, e.g., {'regions': [...], 'companies': [...]}
        """
        pass

    @abstractmethod
    def execute_year_step(self, current_year: int, context: Dict[str, Any]):
        """
        Execute the module's logic for the given simulation year.
        The context provides access to all models, results from other modules in the same step, etc.
        """
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(id='{self.module_id}', name='{self.name}')" 