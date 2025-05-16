from typing import Dict, List, Any
from semiconductor_simulation.core.base_module import BaseModule
from semiconductor_simulation.core.base_model import BaseModel
# Import specific model types if needed for type hinting or direct instantiation, e.g.:
# from semiconductor_simulation.models.region import RegionModel
# from semiconductor_simulation.models.company import CompanyModel

class GeopoliticalModule(BaseModule):
    """
    Simulates geopolitical reshoring, supply chain reconfiguration, policy impacts.
    Operates on RegionModels, CompanyModels, PolicyModels (yet to be defined).
    """
    def __init__(self, module_id: str, name: str = "Geopolitical Dynamics Module"):
        super().__init__(module_id, name)
        self.regions: List[BaseModel] = []
        self.companies: List[BaseModel] = []
        self.policies: List[BaseModel] = [] # Assume PolicyModel will be created

    def initialize(self, models: Dict[str, List[BaseModel]], global_params: Dict[str, Any]):
        """
        Store references to relevant models.
        """
        self.regions = models.get('regions', [])
        self.companies = models.get('companies', [])
        self.policies = models.get('policies', [])
        # print(f"{self.name} initialized with {len(self.regions)} regions, {len(self.companies)} companies.")

    def execute_year_step(self, current_year: int, context: Dict[str, Any]):
        """
        Apply geopolitical logic for the current year.
        - Simulate capacity reallocation from policies (e.g., CHIPS Act).
        - Model trade/export control impacts.
        - Simulate supply chain reorganization (friend-shoring).
        """
        print(f"Executing {self.name} for year {current_year}")

        # --- Simulate CHIPS Act investment distribution (Example Snippet) ---
        # This is a highly simplified example. A real implementation would be complex.
        # It would likely iterate through active PolicyModels that represent CHIPS Acts.
        
        us_chips_act_details = context.get('global_parameters', {}).get('us_chips_act_simulation', {})
        if us_chips_act_details.get('is_active_in_year', lambda y: False)(current_year):
            total_investment_this_year = us_chips_act_details.get('annual_investment_billion', 0)
            node_distribution = us_chips_act_details.get('node_investment_distribution', {})
            geo_focus_ids = us_chips_act_details.get('target_region_ids', []) # e.g. ['usa_arizona', 'usa_ohio']

            # print(f"  {self.name}: Simulating US CHIPS Act investment of ${total_investment_this_year}B")

            for region in self.regions:
                if region.model_id in geo_focus_ids:
                    # print(f"    Applying CHIPS Act funds to {region.name}")
                    current_cap_by_node = region.get_attribute('capacity_by_node')
                    if current_cap_by_node is None: current_cap_by_node = {}
                    
                    for node, percentage in node_distribution.items():
                        investment_for_node = total_investment_this_year * percentage
                        # Simplified: Assume investment directly translates to some capacity increase
                        # A real model needs cost_per_kwpm_for_node, construction_time_lag etc.
                        capacity_increase_kwpm = investment_for_node * us_chips_act_details.get('kwpm_per_billion_invested', 1) 
                        
                        current_cap_by_node[node] = current_cap_by_node.get(node, 0) + capacity_increase_kwpm
                        # print(f"      Increased capacity for {node} in {region.name} by {capacity_increase_kwpm:.2f} KWPM")
                    region.set_attribute('capacity_by_node', current_cap_by_node, current_year)

        # --- Other geopolitical effects ---
        # - Export control impacts on companies/regions
        # - Talent migration modeling
        # - Supply chain reconfigurations (e.g., friend-shoring index for companies)
        
        # Call update_state on affected models (or let them pull data)
        for region in self.regions:
            region.update_state(current_year, context) # Region self-updates based on its new attributes
        for company in self.companies:
            company.update_state(current_year, context) # Company self-updates

        print(f"Finished {self.name} for year {current_year}") 