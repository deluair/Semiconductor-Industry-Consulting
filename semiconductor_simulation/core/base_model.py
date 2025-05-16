from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseModel(ABC):
    """
    Abstract base class for all simulation models (entities or concepts).
    """
    def __init__(self, model_id: str, name: str, initial_attributes: Dict[str, Any] = None):
        self.model_id = model_id
        self.name = name
        self.attributes = initial_attributes if initial_attributes is not None else {}
        self.history = {} # To store attribute changes over time

    @abstractmethod
    def update_state(self, current_year: int, context: Dict[str, Any]):
        """
        Update the model's state for the given year based on the simulation context.
        The context can provide access to other models, global parameters, etc.
        """
        pass

    def get_attribute(self, attribute_name: str, year: int = None):
        """
        Get an attribute's value. If year is specified, tries to get historical value.
        """
        if year is not None and year in self.history and attribute_name in self.history[year]:
            return self.history[year][attribute_name]
        return self.attributes.get(attribute_name)

    def set_attribute(self, attribute_name: str, value: Any, current_year: int):
        """
        Set an attribute's value and record it in history.
        """
        if current_year not in self.history:
            self.history[current_year] = {}
        
        # Store previous value if it's the first change in the current year for this attribute
        if attribute_name not in self.history[current_year] and attribute_name in self.attributes:
             # This logic might need refinement based on how deep history is needed.
             # For simplicity, we assume history[year] stores the state *after* updates in that year.
             pass

        self.attributes[attribute_name] = value
        self.history[current_year][attribute_name] = value

    def __repr__(self):
        return f"{self.__class__.__name__}(id='{self.model_id}', name='{self.name}')" 