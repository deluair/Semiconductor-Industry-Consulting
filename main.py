import argparse
import os
import yaml
from datetime import datetime
from collections import defaultdict

# Adjust imports to reflect the 'semiconductor_simulation' package structure
from semiconductor_simulation.core.simulation_manager import SimulationManager
from semiconductor_simulation.models import RegionModel, CompanyModel, TechnologyNodeModel, EndMarketModel, PolicyModel
from semiconductor_simulation.modules import (
    GeopoliticalModule, CapacityDemandModule, TechEvolutionModule,
    IndustryStructureModule, ConsultingMarketModule, NationalEcosystemModule
)
from semiconductor_simulation.utils.data_loader import load_yaml_data
from semiconductor_simulation.utils.plotter import plot_attribute_over_time, plot_attribute_comparison_over_time
from semiconductor_simulation.utils.report_generator import generate_html_report

# This is the content that will be used to create 'config/scenarios/test_scenario.yaml'
# if it doesn't exist.
# NOTE: Paths for config/results will be relative to where main.py is run (workspace root)
DEFAULT_TEST_SCENARIO_DATA = {
    "scenario_name": "Test Scenario - Initial Setup",
    "simulation_start_year": 2025,
    "simulation_end_year": 2030,
    "global_parameters": {
        "inflation_rate": 0.02,
        "trade_tension_factor": 0.1  # 0: no tension, 1: high tension
    },
    "models_initial_state": {
        "regions": [
            {
                "model_id": "USA", "name": "United States",
                "initial_attributes": {
                    "gdp": 25.0e12, "political_stability": 0.7,
                    "semiconductor_investment_focus": 0.8, "research_funding": 50e9,
                    "water_availability": 0.6, "power_stability": 0.9, "labor_cost": 150000,
                    "environmental_regulations": 0.7, "existing_fab_count": 20,
                    "semiconductor_engineer_count": 70000, "talent_availability": "medium",
                    "talent_notes": "Significant investment via CHIPS Act, but ongoing talent competition."
                }
            },
            {
                "model_id": "China", "name": "China",
                "initial_attributes": {
                    "gdp": 18.0e12, "political_stability": 0.8,
                    "semiconductor_investment_focus": 0.9, "research_funding": 100e9,
                    "water_availability": 0.5, "power_stability": 0.8, "labor_cost": 80000,
                    "environmental_regulations": 0.6, "existing_fab_count": 50,
                    "semiconductor_engineer_count": 200000, "talent_availability": "high",
                    "talent_notes": "Large pool of engineers, strong government push for self-sufficiency."
                }
            },
            {
                "model_id": "EU", "name": "European Union",
                "initial_attributes": {
                    "gdp": 17.0e12, "political_stability": 0.75,
                    "semiconductor_investment_focus": 0.6, "research_funding": 40e9,
                    "water_availability": 0.7, "power_stability": 0.85, "labor_cost": 120000,
                    "environmental_regulations": 0.8, "existing_fab_count": 15,
                    "semiconductor_engineer_count": 50000,
                    "talent_availability": "shortage",
                    "talent_notes": "McKinsey & Synopsys report significant talent gap and need for upskilling. EU Chips Act aims to address this."
                }
            }
        ],
        "companies": [
            {
                "model_id": "CompA", "name": "Alpha Devices",
                "initial_attributes": {
                    "company_type": "IDM", # Added company_type here
                    "region_id": "USA", "specialization": "Leading-Edge Logic",
                    "market_share": 0.20, "rd_intensity": 0.15, "capex": 30e9, "revenue": 150e9,
                    "global_strategy_score": 0.8, "agility_score": 0.7, "supply_chain_resilience": 0.6,
                    "current_node_id": "N3"
                }
            },
            {
                "model_id": "CompB", "name": "Beta Fab",
                "initial_attributes": {
                    "company_type": "Foundry", # Added company_type here
                    "region_id": "China", "specialization": "Mature Node Foundry",
                    "market_share": 0.10, "rd_intensity": 0.05, "capex": 10e9, "revenue": 50e9,
                    "global_strategy_score": 0.5, "agility_score": 0.8, "supply_chain_resilience": 0.7,
                    "current_node_id": "N28"
                }
            }
        ],
        "technology_nodes": [
            {
                "model_id": "N3", "name": "3nm Node",
                "initial_attributes": {
                    "maturity_level": 0.9, "cost_per_wafer": 17000.0, "development_risk": 0.2
                }
            },
            {
                "model_id": "N5", "name": "5nm Node",
                "initial_attributes": {
                     "maturity_level": 1.0, "cost_per_wafer": 12000.0, "development_risk": 0.1
                }
            },
            {
                "model_id": "N28", "name": "28nm Node",
                "initial_attributes": {
                    "maturity_level": 1.0, "cost_per_wafer": 3000.0, "development_risk": 0.05
                }
            }
        ],
        "end_markets": [
            {
                "model_id": "EM1", "name": "Smartphones",
                "initial_attributes": {
                    "size": 700e9, "growth_rate": 0.03,
                    "chip_demand_factor": {"N3": 0.6, "N5": 0.3, "N28": 0.1}
                }
            },
            {
                "model_id": "EM2", "name": "Automotive",
                "initial_attributes": {
                    "size": 300e9, "growth_rate": 0.08,
                    "chip_demand_factor": {"N5": 0.2, "N28": 0.8}
                }
            }
        ],
        "policies": [
            {
                "model_id": "PolicyUSA1", "name": "US CHIPS Act Funding Wave 1",
                "initial_attributes": {
                    "policy_type": "InvestmentIncentive", # Renamed from 'type' and nested
                    "issuing_region_id": "USA", "target_entity_type": "COMPANY", 
                    "target_entity_ids": ["CompA"],
                    "start_year": 2025, "end_year": 2028, "value_impact": 5e9,
                    "conditions": "Focus on leading-edge onshore manufacturing",
                    "current_status": "active" # Note: PolicyModel's update_state manages active status based on year
                }
            },
            {
                "model_id": "PolicyEU1", "name": "EU Chips Act Initial Investment",
                "initial_attributes": {
                    "policy_type": "InvestmentIncentive", # Renamed from 'type' and nested
                    "issuing_region_id": "EU", "target_entity_type": "REGION",
                    "target_entity_ids": ["EU"],
                    "start_year": 2025, "end_year": 2029, "value_impact": 10e9,
                    "conditions": "Strengthen EU semiconductor ecosystem, focus on research and advanced nodes",
                    "current_status": "active"
                }
            }
        ]
    }
}

def bootstrap_config_files():
    """
    Generates example config files if they don't exist.
    """
    config_dir = "config"
    scenarios_dir = os.path.join(config_dir, "scenarios")
    results_dir = "results" # Ensure results directory also exists

    os.makedirs(config_dir, exist_ok=True)
    os.makedirs(scenarios_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True) # Create results dir

    scenario_file_path = os.path.join(scenarios_dir, "test_scenario.yaml")
    base_data_file_path = os.path.join(config_dir, "base_data.yaml")

    if not os.path.exists(scenario_file_path):
        print(f"Generating example scenario file: {scenario_file_path}")
        with open(scenario_file_path, 'w') as f:
            yaml.dump(DEFAULT_TEST_SCENARIO_DATA, f, indent=4, sort_keys=False)

    if not os.path.exists(base_data_file_path):
        print(f"Generating example base data file: {base_data_file_path}")
        example_base_data = {
            "model_lifespans": {
                "default": 10, # years
                "technology_node": 5
            },
            "economic_factors": {
                "global_gdp_growth_baseline": 0.025
            }
        }
        with open(base_data_file_path, 'w') as f:
            yaml.dump(example_base_data, f, indent=4, sort_keys=False)

def transform_yearly_results_to_trajectories(yearly_results: dict) -> dict:
    """
    Transforms simulation results from {year: {category: [model_states]}}
    to {category: {model_id: [{year: year, **attributes}]}}.
    """
    trajectories = defaultdict(lambda: defaultdict(list))
    sorted_years = sorted(yearly_results.keys())

    for year in sorted_years:
        year_data = yearly_results[year]
        for category, model_list in year_data.items():
            for model_state in model_list:
                model_id = model_state['model_id']
                # Add year to the state attributes for the trajectory
                state_with_year = {'year': year, **model_state}
                trajectories[category][model_id].append(state_with_year)
    return dict(trajectories)

def main(scenario_name_arg: str):
    """
    Main function to run the semiconductor industry simulation.
    """
    print(f"Starting simulation for scenario: {scenario_name_arg}")

    bootstrap_config_files()

    # Use scenario_name_arg from the argument for clarity
    scenario_config_path = os.path.join("config", "scenarios", f"{scenario_name_arg}.yaml")
    if not os.path.exists(scenario_config_path):
        print(f"Scenario file {scenario_config_path} not found. Attempting to use test_scenario.yaml.")
        # Fallback to test_scenario.yaml if specific one not found
        # This assumes DEFAULT_TEST_SCENARIO_DATA corresponds to "test_scenario"
        scenario_config_path = os.path.join("config", "scenarios", "test_scenario.yaml")
        # Update scenario_name_arg if we defaulted, so filenames are consistent
        scenario_name_arg = "test_scenario" 
        if not os.path.exists(scenario_config_path):
            print(f"Default test_scenario.yaml also not found after bootstrap. Exiting.")
            return
    
    effective_scenario_name = scenario_name_arg

    sim_manager = SimulationManager(scenario_name=effective_scenario_name) 

    try:
        sim_manager.load_scenario_data(scenario_config_path)
        print(f"Scenario data loaded successfully by SimulationManager for scenario: {effective_scenario_name}")
    except FileNotFoundError:
        print(f"Critical Error: Scenario file {scenario_config_path} not found by SimulationManager. Exiting.")
        return
    except Exception as e:
        print(f"Error loading scenario data via SimulationManager from {scenario_config_path}: {e}")
        return

    sim_manager.register_module(GeopoliticalModule("GeoPol"))
    sim_manager.register_module(CapacityDemandModule("CapDemand"))
    sim_manager.register_module(TechEvolutionModule("TechEvo"))
    sim_manager.register_module(IndustryStructureModule("IndStruct"))
    print("All modules registered.")

    sim_manager.initialize_modules()
    print("All modules initialized by SimulationManager.")

    print(f"Running simulation from {sim_manager.start_year} to {sim_manager.end_year}...")
    # yearly_simulation_results is in the format {year: {category: [model_states]}}
    yearly_simulation_results = sim_manager.run_simulation()
    print("Simulation finished.")

    if not yearly_simulation_results:
        print("Simulation did not produce results. Exiting before processing.")
        return

    # Transform results for report generator and easier access in main.py
    model_trajectories_data = transform_yearly_results_to_trajectories(yearly_simulation_results)

    results_dir = "results"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save the raw yearly_simulation_results
    raw_results_filename = os.path.join(results_dir, f"{effective_scenario_name}_yearly_results_{timestamp}.yaml")
    with open(raw_results_filename, 'w') as f:
        yaml.dump(yearly_simulation_results, f, indent=4, sort_keys=False)
    print(f"Raw yearly simulation results saved to: {raw_results_filename}")

    # Save the transformed model_trajectories_data (optional, but good for inspection)
    trajectories_filename = os.path.join(results_dir, f"{effective_scenario_name}_trajectories_{timestamp}.yaml")
    with open(trajectories_filename, 'w') as f:
        yaml.dump(model_trajectories_data, f, indent=4, sort_keys=False)
    print(f"Transformed model trajectories saved to: {trajectories_filename}")

    plot_filenames = [] 

    # Plotting section: Uses model_trajectories_data for IDs, but passes yearly_simulation_results to plotters
    if "regions" in model_trajectories_data:
        # Get model_ids from the keys of the transformed data
        region_ids = list(model_trajectories_data["regions"].keys())
        if region_ids:
            try:
                gdp_plot_path = plot_attribute_comparison_over_time(
                    results=yearly_simulation_results, # Plotter uses the {year: data} structure
                    model_category="regions",
                    model_ids=region_ids,
                    attribute_name="gdp",
                    scenario_name=sim_manager.scenario_data.get("scenario_name", effective_scenario_name)
                )
                if gdp_plot_path:
                    plot_filenames.append(os.path.basename(gdp_plot_path))
                    print(f"Plot saved for GDP comparison of regions.")

                if "EU" in region_ids:
                    eu_eng_plot_path = plot_attribute_over_time(
                        results=yearly_simulation_results, # Plotter uses the {year: data} structure
                        model_category="regions",
                        model_id="EU",
                        attribute_name="semiconductor_engineer_count",
                        scenario_name=sim_manager.scenario_data.get("scenario_name", effective_scenario_name)
                    )
                    if eu_eng_plot_path:
                        plot_filenames.append(os.path.basename(eu_eng_plot_path))
                        print(f"Plot saved for EU semiconductor_engineer_count.")
            except Exception as e:
                print(f"Error during plotting: {e}")
        else:
            print("No region data to plot (ids derived from trajectories).")
    else:
        print("No region trajectories found in transformed results for plotting.")

    # Prepare data for HTML report
    report_data_package = {
        "scenario_name": sim_manager.scenario_data.get("scenario_name", effective_scenario_name),
        "simulation_start_year": sim_manager.start_year,
        "simulation_end_year": sim_manager.end_year,
        "global_parameters": sim_manager.global_parameters,
        "model_trajectories": model_trajectories_data # Pass the transformed data
    }

    try:
        generate_html_report(
            simulation_results=report_data_package, # Pass the packaged data
            scenario_name=sim_manager.scenario_data.get("scenario_name", effective_scenario_name),
            start_year=sim_manager.start_year,
            end_year=sim_manager.end_year,
            output_dir=results_dir,
            timestamp=timestamp,
            plot_filenames=plot_filenames
        )
    except Exception as e:
        print(f"Error generating HTML report: {e}")

    print("\nSimulation Run Summary:")
    print(f"Years Simulated: {sim_manager.start_year} - {sim_manager.end_year}")
    # Display model counts from sim_manager.models (initial state)
    for model_type, models_list in sim_manager.models.items(): # sim_manager.models is {category: [instances]}
        print(f"Number of {model_type} models: {len(models_list)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Semiconductor Industry Simulation.")
    parser.add_argument("--scenario", type=str, default="test_scenario", dest="scenario_name_arg",
                        help="Name of the scenario YAML file (without .yaml extension) in config/scenarios/")
    args = parser.parse_args()

    main(scenario_name_arg=args.scenario_name_arg) 