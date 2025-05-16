from typing import List, Dict, Any
from semiconductor_simulation.core.base_module import BaseModule
from semiconductor_simulation.core.base_model import BaseModel
from semiconductor_simulation.utils.data_loader import load_yaml_data

# Import all available models for instantiation
from semiconductor_simulation.models import RegionModel, CompanyModel, TechnologyNodeModel, EndMarketModel, PolicyModel
# We will need a way to map model type strings from config to actual classes
MODEL_CLASS_MAP = {
    "RegionModel": RegionModel,
    "CompanyModel": CompanyModel,
    "TechnologyNodeModel": TechnologyNodeModel,
    "EndMarketModel": EndMarketModel,
    "PolicyModel": PolicyModel,
    # Add other models here as they are created, e.g. PolicyModel
}

class SimulationManager:
    """
    Orchestrates the entire simulation process, managing models, modules, time, and scenarios.
    """
    def __init__(self, scenario_name: str, config_base_path: str = "config"):
        self.scenario_name = scenario_name
        self.config_path = config_base_path
        
        self.start_year: int = 0
        self.end_year: int = 0
        self.current_year: int = 0
        
        self.models: Dict[str, List[BaseModel]] = {}
        self.modules: List[BaseModule] = []
        self.results: Dict[int, Dict[str, Any]] = {} 
        self.global_parameters: Dict[str, Any] = {}
        self.scenario_data: Dict[str, Any] = {}

    def load_scenario_data(self, scenario_file_path: str):
        """Loads scenario data directly from a specific file path."""
        print(f"Loading scenario data from: {scenario_file_path}")
        self.scenario_data = load_yaml_data(scenario_file_path)
        self.start_year = self.scenario_data.get('start_year', 2025)
        self.end_year = self.scenario_data.get('end_year', 2040)
        self.current_year = self.start_year
        self.global_parameters = self.scenario_data.get('global_parameters', {})
        self._initialize_models(self.scenario_data.get('models_initial_state', {}))
        print(f"Scenario '{self.scenario_name}' loaded. Simulating from {self.start_year} to {self.end_year}.")

    def _initialize_models(self, models_config: Dict[str, List[Dict[str, Any]]]):
        """Initializes models based on the configuration data."""
        self.models = {}
        for model_type_key, model_list_config in models_config.items():
            # Default heuristic for class name guessing
            class_name_guess = model_type_key.capitalize()[:-1] + "Model"

            # Specific overrides based on the model_type_key from YAML
            if model_type_key == "regions":
                class_name_guess = "RegionModel"
            elif model_type_key == "companies":
                class_name_guess = "CompanyModel"
            elif model_type_key == "technology_nodes":
                class_name_guess = "TechnologyNodeModel"
            elif model_type_key == "end_markets":
                class_name_guess = "EndMarketModel"
            elif model_type_key == "policies":
                class_name_guess = "PolicyModel"
            # Add other specific mappings here if heuristic fails for new model types

            model_class = MODEL_CLASS_MAP.get(class_name_guess)
            
            if not model_class:
                print(f"Warning: No model class found for config key '{model_type_key}' (guessed '{class_name_guess}'). Skipping.")
                continue

            self.models[model_type_key] = []
            for model_data in model_list_config:
                try:
                    # All models now expect model_id, name, and **initial_attributes.
                    # Ensure 'initial_attributes' exists in model_data, or provide an empty dict.
                    # All other keys in model_data (like company_type, region_id, etc.) 
                    # should be nested under 'initial_attributes' in the YAML config.
                    
                    model_id = model_data.get('model_id')
                    name = model_data.get('name')
                    initial_attrs = model_data.get('initial_attributes', {})

                    if not model_id or not name:
                        print(f"Warning: Skipping model data due to missing 'model_id' or 'name': {model_data}")
                        continue
                    
                    # The **initial_attrs will unpack the dictionary.
                    instance = model_class(
                        model_id=model_id,
                        name=name,
                        **initial_attrs
                    )
                    self.models[model_type_key].append(instance)
                except KeyError as e:
                    print(f"Error initializing model {model_data.get('name', '?')}: Missing key {e} in model_data or initial_attributes.")
                except TypeError as e:
                    print(f"Error initializing model {model_data.get('name', '?')} with class {model_class.__name__}: {e}. Check __init__ signature and if all required attributes are in 'initial_attributes' in your YAML.")
                except Exception as e:
                    print(f"General error initializing model {model_data.get('name', '?')}: {e}")
            
            print(f"Initialized {len(self.models[model_type_key])} models of type {model_class.__name__} under key '{model_type_key}'")

    def register_module(self, module: BaseModule):
        """Adds a simulation module to the manager."""
        self.modules.append(module)
        print(f"Registered module: {module.name}")

    def initialize_modules(self):
        """Initializes all registered modules."""
        if not self.models and not self.global_parameters:
            print("Warning: Models and global parameters not loaded before initializing modules. Call load_scenario_data() first.")
            return
        for module in self.modules:
            module.initialize(self.models, self.global_parameters)
        print("All modules initialized.")

    def run_simulation(self):
        """
        Runs the simulation from start_year to end_year.
        """
        if not self.scenario_data:
            print("Error: Scenario data not loaded. Call load_scenario_data() first.")
            return None
            
        print(f"Starting simulation for scenario '{self.scenario_name}' from {self.start_year} to {self.end_year}")
        for year in range(self.start_year, self.end_year + 1):
            self.current_year = year
            print(f"--- Simulating Year: {self.current_year} ---")
            
            yearly_context = {
                'current_year': self.current_year,
                'models': self.models,
                'global_parameters': self.global_parameters,
                'previous_results': self.results.get(year -1, {}),
                'all_results': self.results # Access to all historical results
            }
            
            for module in self.modules:
                module.execute_year_step(self.current_year, yearly_context)
            
            self._collect_yearly_results()
            print(f"--- Completed Year: {self.current_year} ---")
        
        print("Simulation completed.")
        return self.results

    def _collect_yearly_results(self):
        """Collects and stores results for the current year from models."""
        current_year_results = {}
        for model_category, model_list in self.models.items():
            category_results = []
            for model_instance in model_list:
                # Make sure all attributes are serializable for potential output to JSON/YAML
                serializable_attributes = {k: str(v) if isinstance(v, (list, dict)) else v 
                                           for k, v in model_instance.attributes.items()}
                category_results.append({
                    'model_id': model_instance.model_id, 
                    'name': model_instance.name, 
                    **serializable_attributes
                })
            current_year_results[model_category] = category_results
        self.results[self.current_year] = current_year_results

    def get_results(self):
        return self.results 