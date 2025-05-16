class RegionModel(BaseModel):
    """
    Represents a geographical region in the simulation.
    """
    def __init__(self, model_id: str, name: str, gdp: float, political_stability: float,
                 semiconductor_investment_focus: float, research_funding: float,
                 water_availability: float, power_stability: float, labor_cost: float,
                 environmental_regulations: float, existing_fab_count: int,
                 semiconductor_engineer_count: int = 0,
                 talent_availability: str = "medium", # e.g., "high", "medium", "low", "shortage"
                 talent_notes: str = "",
                 **kwargs):
        super().__init__(model_id)
        self.name = name
        # Economic Factors
        self.gdp = gdp  # Current Gross Domestic Product
        self.political_stability = political_stability  # Index from 0 (low) to 1 (high)
        # Industry & Innovation
        self.semiconductor_investment_focus = semiconductor_investment_focus # 0-1, propensity to invest in semis
        self.research_funding = research_funding  # Annual $ in semiconductor research
        # Infrastructure & Resources
        self.water_availability = water_availability # Index 0-1
        self.power_stability = power_stability # Index 0-1
        # Labor & Regulations
        self.labor_cost = labor_cost # Average cost per engineer/year
        self.environmental_regulations = environmental_regulations # Index 0-1, higher is stricter
        # Current State
        self.existing_fab_count = existing_fab_count # Number of operational fabs

        # New attributes for talent
        self.semiconductor_engineer_count = semiconductor_engineer_count
        self.talent_availability = talent_availability
        self.talent_notes = talent_notes

        self.attributes_history.append(self._capture_attributes())

    def _capture_attributes(self):
        return {
            "name": self.name,
            "gdp": self.gdp,
            "political_stability": self.political_stability,
            "semiconductor_investment_focus": self.semiconductor_investment_focus,
            "research_funding": self.research_funding,
            "water_availability": self.water_availability,
            "power_stability": self.power_stability,
            "labor_cost": self.labor_cost,
            "environmental_regulations": self.environmental_regulations,
            "existing_fab_count": self.existing_fab_count,
            "semiconductor_engineer_count": self.semiconductor_engineer_count,
            "talent_availability": self.talent_availability,
            "talent_notes": self.talent_notes,
        }

    def update_state(self, yearly_context: Dict[str, Any]):
        # Implementation of update_state method
        pass 