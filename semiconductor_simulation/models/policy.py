from typing import Dict, Any, Literal, List
from semiconductor_simulation.core.base_model import BaseModel

PolicyType = Literal[
    "InvestmentIncentive", # e.g., CHIPS Act grants
    "ExportControl",       # e.g., Equipment restrictions
    "TradeTariff",         # e.g., Tariffs on specific goods
    "R&DGrant",            # e.g., Funding for research consortia
    "TalentDevelopment",   # e.g., Programs for workforce training
    "IPProtectionLaw",     # e.g., Changes to IP regimes
    "NationalSecurityReview" # e.g., FDI screening
]

TargetEntityType = Literal["Region", "Company", "TechnologyNode", "EndMarket", "Global"]

class PolicyModel(BaseModel):
    """
    Represents a governmental or inter-governmental policy that impacts the semiconductor industry.
    The 'policy_type' attribute is crucial and should be provided in initial_attributes.
    Other expected initial_attributes could include: enacting_region_id, start_year, end_year, 
    target_entities, target_entity_types, description, and type-specific attributes like 
    total_funding_billion_usd for InvestmentIncentive, or restricted_technologies for ExportControl.
    """
    def __init__(self, model_id: str, name: str, **initial_attributes: Any):
        super().__init__(model_id, name, initial_attributes)
        # Ensure 'policy_type' is present.
        if 'policy_type' not in self.attributes:
            print(f"Warning: PolicyModel '{name}' (ID: {model_id}) initialized without 'policy_type' in initial_attributes.")
            self.attributes['policy_type'] = None # Or some default, or raise error

        # Other attributes are handled by BaseModel via initial_attributes.
        # Example type-specific defaults or checks could be done here if needed:
        # policy_type = self.get_attribute('policy_type')
        # if policy_type == "InvestmentIncentive" and 'total_funding_billion_usd' not in self.attributes:
        #     self.attributes['total_funding_billion_usd'] = 0

    def update_state(self, current_year: int, context: Dict[str, Any]):
        """
        Update policy's state. For example, check if it becomes active/inactive.
        Most policy impacts are handled by other modules reacting to active policies.
        """
        start_year = self.get_attribute('start_year')
        end_year = self.get_attribute('end_year')
        
        is_active_now = True
        if start_year is not None and current_year < start_year:
            is_active_now = False
        if end_year is not None and current_year > end_year:
            is_active_now = False
        
        if self.get_attribute('is_active') != is_active_now:
            self.set_attribute('is_active', is_active_now, current_year)
            # print(f"Policy '{self.name}' active status changed to: {is_active_now} in year {current_year}")

        # Some policies might have internal state changes, e.g., depleting funds
        # if self.get_attribute('policy_type') == "InvestmentIncentive" and self.get_attribute('is_active'):
        #     disbursed_this_year = self.get_attribute('annual_disbursement_rate_billion_usd', 0) # Example attribute
        #     current_disbursed = self.get_attribute('funding_disbursed_to_date_billion_usd', 0)
        #     total_funding = self.get_attribute('total_funding_billion_usd', 0)
        #     actual_disbursement = min(disbursed_this_year, total_funding - current_disbursed)
        #     if actual_disbursement > 0:
        #        self.set_attribute('funding_disbursed_to_date_billion_usd', current_disbursed + actual_disbursement, current_year)
        #        # print(f"Policy '{self.name}' disbursed ${actual_disbursement}B this year.")
        pass

    def is_policy_active(self, current_year: int) -> bool:
        """Helper method to check if policy is active in a given year."""
        start = self.get_attribute('start_year')
        end = self.get_attribute('end_year')
        active = True
        if start and current_year < start:
            active = False
        if end and current_year > end:
            active = False
        return active 