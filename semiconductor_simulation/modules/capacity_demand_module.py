from typing import Dict, List, Any
from semiconductor_simulation.core.base_module import BaseModule
from semiconductor_simulation.core.base_model import BaseModel
# from semiconductor_simulation.models.company import CompanyModel
# from semiconductor_simulation.models.technology_node import TechnologyNodeModel
# from semiconductor_simulation.models.end_market import EndMarketModel

class CapacityDemandModule(BaseModule):
    """
    Simulates the balance between semiconductor manufacturing capacity and market demand.
    It affects pricing, investment decisions, and capacity allocation.
    Operates on CompanyModels (foundries, IDMs), TechnologyNodeModels, and EndMarketModels.
    """
    def __init__(self, module_id: str, name: str = "Capacity-Demand Balancing Module"):
        super().__init__(module_id, name)
        self.companies: List[BaseModel] = []
        self.tech_nodes: List[BaseModel] = []
        self.end_markets: List[BaseModel] = []

    def initialize(self, models: Dict[str, List[BaseModel]], global_params: Dict[str, Any]):
        """
        Store references to relevant models.
        """
        self.companies = models.get('companies', [])
        self.tech_nodes = models.get('tech_nodes', [])
        self.end_markets = models.get('end_markets', [])
        # print(f"{self.name} initialized with {len(self.companies)} companies, "
        #       f"{len(self.tech_nodes)} tech_nodes, {len(self.end_markets)} end_markets.")

    def execute_year_step(self, current_year: int, context: Dict[str, Any]):
        """
        Apply capacity-demand balancing logic for the current year.
        1. Aggregate total demand per node from EndMarketModels.
        2. Aggregate total supply per node from CompanyModels (Foundries, IDMs).
        3. Calculate supply-demand gap per node.
        4. Adjust prices on TechnologyNodeModels based on gap (simplified).
        5. Influence company investment decisions (future capacity) based on gap and profitability (simplified).
        6. Allocate available capacity to customers/end-markets (highly complex, placeholder).
        """
        print(f"Executing {self.name} for year {current_year}")

        # --- 1. Aggregate total demand per node ---
        total_demand_per_node_kwpm: Dict[str, float] = {}
        for market in self.end_markets:
            # Assume market.attributes['base_demand_wafer_starts_kwpm'] is like {'3nm': 20, '5nm': 30}
            # Assume market.attributes['node_demand_split_percentage'] for $ demand conversion if needed
            market_demand_kwpm = market.get_attribute('base_demand_wafer_starts_kwpm')
            if isinstance(market_demand_kwpm, dict):
                for node_id, demand in market_demand_kwpm.items():
                    total_demand_per_node_kwpm[node_id] = total_demand_per_node_kwpm.get(node_id, 0) + float(demand)
        # print(f"  {self.name}: Total demand per node (KWPM): {total_demand_per_node_kwpm}")

        # --- 2. Aggregate total supply per node ---
        total_supply_per_node_kwpm: Dict[str, float] = {}
        for company in self.companies:
            company_type = company.get_attribute('company_type')
            if company_type in ["Foundry", "IDM"]:
                # Assume company.attributes['fab_capacity_kwpm_by_node'] is like {'3nm': 50, '28nm': 100}
                fab_capacity = company.get_attribute('fab_capacity_kwpm_by_node')
                if isinstance(fab_capacity, dict):
                    for node_id, capacity in fab_capacity.items():
                        total_supply_per_node_kwpm[node_id] = total_supply_per_node_kwpm.get(node_id, 0) + float(capacity)
        # print(f"  {self.name}: Total supply per node (KWPM): {total_supply_per_node_kwpm}")

        # --- 3. Calculate supply-demand gap per node ---
        supply_demand_gap_kwpm: Dict[str, float] = {}
        all_nodes = set(total_demand_per_node_kwpm.keys()) | set(total_supply_per_node_kwpm.keys())
        for node_id in all_nodes:
            demand = total_demand_per_node_kwpm.get(node_id, 0)
            supply = total_supply_per_node_kwpm.get(node_id, 0)
            supply_demand_gap_kwpm[node_id] = supply - demand
        # print(f"  {self.name}: Supply-Demand Gap per node (KWPM): {supply_demand_gap_kwpm}")

        # --- 4. Adjust prices on TechnologyNodeModels (simplified) ---
        for tech_node in self.tech_nodes:
            gap = supply_demand_gap_kwpm.get(tech_node.model_id, 0)
            current_price = tech_node.get_attribute('average_price_per_wafer_usd')
            price_sensitivity = context.get('global_parameters', {}).get('price_sensitivity_to_gap', 0.01) # e.g. 1% price change per 10KWPM gap

            if current_price is not None:
                # If demand > supply (gap < 0), price increases. If supply > demand (gap > 0), price decreases.
                price_change_factor = -gap * price_sensitivity 
                new_price = float(current_price) * (1 + price_change_factor)
                tech_node.set_attribute('average_price_per_wafer_usd', max(0, new_price), current_year) # Price cannot be negative
                # print(f"    Node {tech_node.name}: Gap {gap:.2f} KWPM, Price updated from ${current_price:.2f} to ${new_price:.2f}")

        # --- 5. Influence company investment decisions (highly simplified placeholder) ---
        # For companies (Foundries, IDMs), if gap is negative (shortage) for their focused nodes, 
        # they might increase an 'investment_inclination' attribute, which TechEvolutionModule or 
        # IndustryStructureModule could later use to simulate actual capacity expansion (with time lags).
        # This is a very coarse representation.

        # --- 6. Allocate available capacity (placeholder) ---
        # This is a very complex step involving customer priorities, LTAs, pricing, etc.
        # For now, we assume demand is met if supply is sufficient, or rationed proportionally if not.

        # Update model states that might have changed directly in this module
        for market in self.end_markets:
            market.update_state(current_year, context)
        for tech_node in self.tech_nodes:
            tech_node.update_state(current_year, context)
        for company in self.companies:
            company.update_state(current_year, context)

        print(f"Finished {self.name} for year {current_year}") 