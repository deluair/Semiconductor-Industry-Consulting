import matplotlib.pyplot as plt
from typing import Dict, Any, List
import os

# Ensure results directory exists
RESULTS_DIR = "results"

def plot_attribute_over_time(
    results: Dict[int, Dict[str, Any]], 
    model_category: str, # e.g., 'regions', 'companies', 'tech_nodes'
    model_id: str, 
    attribute_name: str, 
    scenario_name: str = "scenario"
):
    """
    Plots a specific attribute of a specific model instance over time.
    Example: Plot 'talent_pool_skilled_engineers' for region 'usa'.
    Example: Plot 'average_price_per_wafer_usd' for tech_node '3nm'.
    """
    years = sorted(results.keys())
    values = []
    model_name_for_plot = model_id # Default

    for year in years:
        year_data = results[year]
        if model_category in year_data:
            models_in_category = year_data[model_category]
            found_model = None
            for model_data in models_in_category:
                if model_data.get('model_id') == model_id:
                    found_model = model_data
                    model_name_for_plot = model_data.get('name', model_id)
                    break
            
            if found_model:
                try:
                    value = found_model.get(attribute_name)
                    if value is not None:
                        values.append(float(value)) # Ensure it's a number
                    else:
                        values.append(None) # Keep placeholder for missing data points
                except (ValueError, TypeError):
                    values.append(None) # If conversion to float fails
            else:
                values.append(None) # Model not found in this year for this category
        else:
            values.append(None) # Category not found for this year

    # Filter out years where data might be None if necessary, or plot with gaps
    plottable_years = []
    plottable_values = []
    for i, val in enumerate(values):
        if val is not None:
            plottable_years.append(years[i])
            plottable_values.append(val)

    if not plottable_values:
        print(f"No data found for {attribute_name} of {model_id} in {model_category} to plot.")
        return None # Return None if no plot generated

    plt.figure(figsize=(10, 6))
    plt.plot(plottable_years, plottable_values, marker='o', linestyle='-')
    plt.title(f"{attribute_name.replace('_', ' ').title()} for {model_name_for_plot} ({model_category[:-1]})\nScenario: {scenario_name}")
    plt.xlabel("Year")
    plt.ylabel(attribute_name.replace('_', ' ').title())
    plt.grid(True)
    plt.xticks(plottable_years) # Ensure all years with data are ticked
    plt.tight_layout()
    
    plot_filename = f"{scenario_name}_{model_category}_{model_id}_{attribute_name}.png"
    os.makedirs(RESULTS_DIR, exist_ok=True)
    save_path = os.path.join(RESULTS_DIR, plot_filename)
    try:
        plt.savefig(save_path)
        print(f"Plot saved to {save_path}")
        return save_path # Return the path where the plot was saved
    except Exception as e:
        print(f"Error saving plot {save_path}: {e}")
        return None # Return None on error
    finally:
        plt.close() # Ensure plot is closed


# Example of a more complex plot: comparing an attribute across multiple models in the same category
def plot_attribute_comparison_over_time(
    results: Dict[int, Dict[str, Any]],
    model_category: str, # e.g., 'companies'
    model_ids: List[str], # List of model_ids to compare, e.g. ['comp_a', 'comp_b']
    attribute_name: str,
    scenario_name: str = "scenario"
):
    """Plots an attribute for multiple models of the same category over time."""
    plt.figure(figsize=(12, 7))
    years = sorted(results.keys())
    
    all_series_empty = True

    for model_id_to_plot in model_ids:
        values = []
        model_name_for_legend = model_id_to_plot
        for year in years:
            year_data = results[year]
            model_instance_data = None
            if model_category in year_data:
                for m_data in year_data[model_category]:
                    if m_data.get('model_id') == model_id_to_plot:
                        model_instance_data = m_data
                        model_name_for_legend = m_data.get('name', model_id_to_plot)
                        break
            
            if model_instance_data and model_instance_data.get(attribute_name) is not None:
                try:
                    values.append(float(model_instance_data.get(attribute_name)))
                except (ValueError, TypeError):
                    values.append(None)
            else:
                values.append(None)
        
        plottable_years_series = []
        plottable_values_series = []
        for i, val in enumerate(values):
            if val is not None:
                plottable_years_series.append(years[i])
                plottable_values_series.append(val)

        if plottable_values_series:
            all_series_empty = False
            plt.plot(plottable_years_series, plottable_values_series, marker='o', linestyle='-', label=f"{model_name_for_legend}")

    if all_series_empty:
        print(f"No data found for attribute {attribute_name} for any of the specified models in {model_category}.")
        plt.close()
        return None # Return None if no plot generated

    plt.title(f"{attribute_name.replace('_', ' ').title()} Comparison for {model_category.title()}\nScenario: {scenario_name}")
    plt.xlabel("Year")
    plt.ylabel(attribute_name.replace('_', ' ').title())
    plt.grid(True)
    plt.xticks(years)
    plt.legend()
    plt.tight_layout()

    plot_filename = f"{scenario_name}_{model_category}_comparison_{attribute_name}.png"
    os.makedirs(RESULTS_DIR, exist_ok=True)
    save_path = os.path.join(RESULTS_DIR, plot_filename)
    try:
        plt.savefig(save_path)
        print(f"Plot saved to {save_path}")
        return save_path # Return the path where the plot was saved
    except Exception as e:
        print(f"Error saving plot {save_path}: {e}")
        return None # Return None on error
    finally:
        plt.close() # Ensure plot is closed

if __name__ == '__main__':
    # This is for direct testing of plotter.py. 
    # It needs a sample results structure (e.g., from a previous simulation run saved as YAML)
    print("Plotter direct test requires a sample results YAML file (e.g., results/test_scenario_results.yaml)")
    print("Run main.py first to generate sample results.")
    
    # Example: Load results and try to plot something
    # from semiconductor_simulation.utils.data_loader import load_yaml_data
    # sample_results_file = os.path.join(RESULTS_DIR, "test_scenario_results.yaml")
    # if os.path.exists(sample_results_file):
    #     print(f"Loading sample results from {sample_results_file}")
    #     sample_results = load_yaml_data(sample_results_file)
    #     if sample_results:
    #         plot_attribute_over_time(sample_results, 'regions', 'usa', 'talent_pool_skilled_engineers', scenario_name='test_scenario_direct_plot')
    #         plot_attribute_over_time(sample_results, 'tech_nodes', '3nm', 'average_price_per_wafer_usd', scenario_name='test_scenario_direct_plot')
    #         plot_attribute_comparison_over_time(sample_results, 'companies', ['comp_a', 'comp_b'], 'revenue_billion_usd', scenario_name='test_scenario_direct_plot')
    # else:
    #     print(f"Sample results file {sample_results_file} not found. Run main.py to generate it.")
    pass 