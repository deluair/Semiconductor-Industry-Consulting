import yaml
from typing import Dict, Any, List
import os

def load_yaml_data(file_path: str) -> Dict[str, Any]:
    """Loads data from a YAML file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: YAML file not found at {file_path}")
    try:
        with open(file_path, 'r') as stream:
            data = yaml.safe_load(stream)
        return data if data is not None else {}
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML file {file_path}: {exc}")
        # Potentially re-raise or handle more gracefully
        raise
    except Exception as e:
        print(f"An unexpected error occurred while loading YAML file {file_path}: {e}")
        raise

def load_scenario_config(scenario_name: str, config_path: str = "config/scenarios") -> Dict[str, Any]:
    """Loads a specific scenario configuration file."""
    file_path = os.path.join(config_path, f"{scenario_name}.yaml")
    return load_yaml_data(file_path)

def load_base_data(base_data_file: str = "config/base_data.yaml") -> Dict[str, Any]:
    """
    Loads base simulation data, which might include initial model attributes common across scenarios,
    or default global parameters.
    """
    return load_yaml_data(base_data_file)

# Example usage (for testing, typically called from SimulationManager or main script):
if __name__ == '__main__':
    # Create dummy files for testing
    os.makedirs("config/scenarios", exist_ok=True)
    with open("config/base_data.yaml", "w") as f:
        yaml.dump({
            "global_parameters": {"sim_version": "0.1"},
            "model_defaults": {"region": {"default_gdp": 1.0}}
            }, f)
    
    with open("config/scenarios/test_scenario.yaml", "w") as f:
        yaml.dump({
            "scenario_description": "A test scenario.",
            "start_year": 2025,
            "end_year": 2030,
            "global_parameters": {"talent_growth_rate": 0.02},
            "models_initial_state": {
                "regions": [
                    {"model_id": "usa", "name": "United States", "initial_attributes": {"gdp_trillion_usd": 25.0, "talent_pool_skilled_engineers": 50000}}
                ],
                "companies": [
                    {"model_id": "comp_a", "name": "Alpha Foundry", "company_type": "Foundry", "initial_attributes": {"revenue_billion_usd": 10}}
                ]
            }
        }, f)

    try:
        base_config = load_base_data()
        print(f"Base Config Loaded: {base_config}")
        test_scenario_data = load_scenario_config("test_scenario")
        print(f"Test Scenario Data Loaded: {test_scenario_data}")
    except Exception as e:
        print(f"Error during test loading: {e}")
    finally:
        # Clean up dummy files
        # os.remove("config/base_data.yaml")
        # os.remove("config/scenarios/test_scenario.yaml")
        # if not os.listdir("config/scenarios"):
        #     os.rmdir("config/scenarios")
        # if not os.listdir("config"):
        #    os.rmdir("config")
        pass # Keep files for now to allow user to inspect 