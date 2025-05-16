import os
import yaml # For potentially saving results
from semiconductor_simulation.core import SimulationManager
# Import all available modules to register them
from semiconductor_simulation.modules import (
    GeopoliticalModule, 
    CapacityDemandModule, 
    TechEvolutionModule, 
    IndustryStructureModule,
    ConsultingMarketModule,
    NationalEcosystemModule
)

def run_test_simulation(scenario_name: str = "test_scenario"):
    """Runs a single simulation scenario."""
    print(f"Attempting to run simulation for scenario: {scenario_name}")
    
    # Construct the scenario file path
    # Assumes main.py is in the root of the semiconductor_simulation project 
    # or the config path is correctly relative to the CWD.
    # For robustness, one might use absolute paths or more sophisticated path management.
    scenario_file_path = os.path.join("config", "scenarios", f"{scenario_name}.yaml")

    if not os.path.exists(scenario_file_path):
        print(f"Error: Scenario file not found at {scenario_file_path}")
        print("Please ensure you have run semiconductor_simulation/utils/data_loader.py once to create dummy config files if they don\'t exist.")
        return

    sim_manager = SimulationManager(scenario_name=scenario_name)
    
    try:
        sim_manager.load_scenario_data(scenario_file_path=scenario_file_path)
    except FileNotFoundError as e:
        print(e)
        return
    except Exception as e:
        print(f"Error loading scenario data: {e}")
        return

    # Register modules
    sim_manager.register_module(GeopoliticalModule(module_id="GEO"))
    sim_manager.register_module(CapacityDemandModule(module_id="CAPDEM"))
    sim_manager.register_module(TechEvolutionModule(module_id="TECHEVO"))
    sim_manager.register_module(IndustryStructureModule(module_id="INDSTR"))
    sim_manager.register_module(ConsultingMarketModule(module_id="CONSULT"))
    sim_manager.register_module(NationalEcosystemModule(module_id="NATECO"))
    
    sim_manager.initialize_modules()
    
    results = sim_manager.run_simulation()
    
    if results:
        print("\n--- Simulation Results Summary ---")
        for year, yearly_data in results.items():
            print(f"\nYear: {year}")
            for model_category, model_instances in yearly_data.items():
                print(f"  {model_category.capitalize()}:")
                for instance_data in model_instances:
                    # Print only a few key attributes for brevity
                    print(f"    - {instance_data.get('name')} (ID: {instance_data.get('model_id')})") # Attributes: {instance_data}")
        
        # Save results to a YAML file
        results_dir = "results"
        os.makedirs(results_dir, exist_ok=True)
        results_file_path = os.path.join(results_dir, f"{scenario_name}_results.yaml")
        try:
            with open(results_file_path, 'w') as f:
                yaml.dump(results, f, indent=2, sort_keys=False)
            print(f"\nFull results saved to: {results_file_path}")
        except Exception as e:
            print(f"Error saving results: {e}")

        # --- Add Plotting Example --- 
        try:
            from semiconductor_simulation.utils.plotter import plot_attribute_over_time, plot_attribute_comparison_over_time
            print("\n--- Generating Plots ---")
            # Plot some example attributes if the models and attributes exist
            if 'regions' in results[sim_manager.start_year] and any(r['model_id'] == 'usa' for r in results[sim_manager.start_year]['regions']):
                plot_attribute_over_time(results, 'regions', 'usa', 'talent_pool_skilled_engineers', scenario_name=scenario_name)
            
            if 'tech_nodes' in results[sim_manager.start_year] and any(tn['model_id'] == '3nm' for tn in results[sim_manager.start_year]['tech_nodes']):
                 plot_attribute_over_time(results, 'tech_nodes', '3nm', 'average_price_per_wafer_usd', scenario_name=scenario_name)
                 plot_attribute_over_time(results, 'tech_nodes', '3nm', 'maturity_trl', scenario_name=scenario_name)

            company_ids_to_plot = []
            if 'companies' in results[sim_manager.start_year]:
                company_ids_to_plot = [c['model_id'] for c in results[sim_manager.start_year]['companies'] 
                                       if c.get('company_type') == 'Foundry' or c.get('company_type') == 'Fabless']
            if len(company_ids_to_plot) > 0:
                plot_attribute_comparison_over_time(results, 'companies', company_ids_to_plot, 'revenue_billion_usd', scenario_name=scenario_name)

        except ImportError:
            print("Plotter utility not found, skipping plot generation.")
        except Exception as e:
            print(f"Error during plot generation: {e}")
    else:
        print("Simulation did not produce results.")

if __name__ == "__main__":
    # Ensure the dummy config files from data_loader.py exist if running main.py directly after git clone
    # Normally, data_loader.py would be run or its test part would be integrated differently.
    try:
        from semiconductor_simulation.utils.data_loader import load_base_data, load_scenario_config
        if not os.path.exists("config/base_data.yaml") or not os.path.exists("config/scenarios/test_scenario.yaml"):
            print("Initial configuration files not found. Attempting to create them...")
            # This is a bit of a hack for self-contained running. 
            # In a real setup, config files would be managed separately.
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
                    "end_year": 2026, # Shortened for quick test
                    "global_parameters": {
                        "talent_growth_rate": 0.02, 
                        "price_sensitivity_to_gap": 0.005, 
                        "rd_effectiveness_factor": 0.05,
                        "us_chips_act_simulation": {
                            "annual_investment_billion": 5,
                            "node_investment_distribution": {"3nm": 0.6, "7nm": 0.4},
                            "target_region_ids": ["usa"],
                            "kwpm_per_billion_invested": 0.5
                        }
                    },
                    "models_initial_state": {
                        "regions": [
                            {"model_id": "usa", "name": "United States", "initial_attributes": {"gdp_trillion_usd": 25.0, "talent_pool_skilled_engineers": 50000, "capacity_by_node_kwpm": {"7nm": 5, "28nm": 50}}},
                            {"model_id": "eu", "name": "European Union", "initial_attributes": {"gdp_trillion_usd": 18.0, "talent_pool_skilled_engineers": 40000, "capacity_by_node_kwpm": {"28nm": 60}}}
                        ],
                        "companies": [
                            {"model_id": "comp_a", "name": "Alpha Foundry", "company_type": "Foundry", "initial_attributes": {"revenue_billion_usd": 10, "fab_capacity_kwpm_by_node": {"7nm": 5, "28nm": 30}, "primary_node_focus": ["7nm"]}},
                            {"model_id": "comp_b", "name": "Beta Fabless", "company_type": "Fabless", "initial_attributes": {"revenue_billion_usd": 5}},
                            {"model_id": "consult_x", "name": "Future Horizons Consulting", "company_type": "Consultancy", "initial_attributes": {"geopolitical_expertise_score": 3, "technical_semiconductor_knowledge_score": 4}}
                        ],
                        "tech_nodes": [
                            {"model_id": "3nm", "name": "3nm Node", "initial_attributes": {"maturity_trl": 6, "average_price_per_wafer_usd": 15000, "year_commercialized": None, "commercialization_trl_threshold": 8}},
                            {"model_id": "7nm", "name": "7nm Node", "initial_attributes": {"maturity_trl": 9, "average_price_per_wafer_usd": 8000, "year_commercialized": 2020}},
                            {"model_id": "28nm", "name": "28nm Node", "initial_attributes": {"maturity_trl": 9, "average_price_per_wafer_usd": 3000, "year_commercialized": 2011}}
                        ],
                        "end_markets": [
                            {"model_id": "ai_high_perf", "name": "AI & High Performance Computing", "initial_attributes": {"base_demand_wafer_starts_kwpm": {"3nm": 1, "7nm": 3}, "annual_growth_rate_kwpm": {"3nm": 0.20, "7nm": 0.15}}},
                            {"model_id": "automotive", "name": "Automotive", "initial_attributes": {"base_demand_wafer_starts_kwpm": {"28nm": 15, "7nm": 1}, "annual_growth_rate_kwpm": {"28nm": 0.05, "7nm": 0.10}}}
                        ],
                        "policies": [
                            {
                                "model_id": "us_chips_act_grant", 
                                "name": "US CHIPS Act Grant Program", 
                                "policy_type": "InvestmentIncentive",
                                "initial_attributes": {
                                    "enacting_region_id": "usa",
                                    "start_year": 2025,
                                    "end_year": 2029,
                                    "total_funding_billion_usd": 39,
                                    "annual_disbursement_billion_usd": 7.8, # Simplified even disbursement
                                    "funding_disbursed_to_date_billion_usd": 0,
                                    "target_entity_types": ["Region", "Company"],
                                    "description": "Grants for semiconductor manufacturing in the US.",
                                    "funding_distribution_rules": { # Example rules, interpretation up to GeopoliticalModule
                                        "node_focus": {"leading_edge": 0.6, "mature_node": 0.3, "packaging": 0.1},
                                        "target_regions_explicit": ["usa_arizona", "usa_ohio", "usa_texas"] # Example sub-regions if used
                                    }
                                }
                            },
                            {
                                "model_id": "euv_export_restriction_alpha",
                                "name": "Alpha Restriction on EUV Exports",
                                "policy_type": "ExportControl",
                                "initial_attributes": {
                                    "enacting_region_id": "alpha_country_group", # Could be a group or specific country
                                    "start_year": 2026,
                                    "restricted_technologies": ["EUV_tools_gen2"], # Keyword for tech
                                    "affected_regions": ["target_region_x", "target_region_y"],
                                    "description": "Restrictions on export of Gen2 EUV lithography tools.",
                                    "enforcement_level_score": 0.9
                                }
                            }
                        ]
                    }
                }, f)
            print("Dummy config files created/verified.")
    except ImportError:
        print("Warning: Could not import data_loader to create dummy files. Ensure PYTHONPATH is set correctly or run utils/data_loader.py manually once.")
    except Exception as e:
        print(f"Error during pre-run config check: {e}")

    run_test_simulation(scenario_name="test_scenario") 