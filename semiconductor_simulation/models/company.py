from typing import Dict, Any, Literal, List
from semiconductor_simulation.core.base_model import BaseModel

CompanyType = Literal["Foundry", "Fabless", "IDM", "EquipmentSupplier", "OSAT", "Consultancy", "MaterialsSupplier"]

class CompanyModel(BaseModel):
    """
    Represents a company in the semiconductor ecosystem.
    Expected initial_attributes keys: company_type, market_share, revenue, R&D spend, 
    capacity (if applicable), partnerships, etc.
    The 'company_type' attribute is crucial and should be provided in initial_attributes.
    """
    def __init__(self, model_id: str, name: str, **initial_attributes: Any):
        super().__init__(model_id, name, initial_attributes)
        # Ensure 'company_type' is present, as it's fundamental for CompanyModel.
        # Modules relying on company_type will expect it in self.attributes.
        if 'company_type' not in self.attributes:
            # Or raise an error, or set a default if a sensible one exists.
            # For now, let's print a warning if it's missing. Ideally, config validation catches this.
            print(f"Warning: CompanyModel '{name}' (ID: {model_id}) initialized without 'company_type' in initial_attributes.")
            self.attributes['company_type'] = None # Or some default

        # Example attributes that might be set based on company_type if not in initial_attributes:
        # company_type = self.get_attribute('company_type')
        # if company_type in ["Foundry", "IDM"] and 'fab_capacity_kwpm_by_node' not in self.attributes:
        #     self.attributes.setdefault('fab_capacity_kwpm_by_node', {})
        
        # --- The rest of the initial_attributes are handled by BaseModel ---

    def update_state(self, current_year: int, context: Dict[str, Any]):
        """
        Update company's state. 
        Example: Revenue might change based on market conditions, investments might yield new capacity.
        Logic driven by modules like CapacityDemandModule, MarketStructureModule.
        """
        # print(f"Updating state for Company: {self.name} ({self.attributes.get('company_type')}) in year {current_year}")
        # Placeholder logic
        # company_type = self.get_attribute('company_type')
        # if company_type in ["Foundry", "IDM"]:
        #    fab_capacity = self.get_attribute('fab_capacity_kwpm_by_node')
             # Update capacity based on investments, deprecation etc.
        pass # Actual logic will be complex and driven by modules