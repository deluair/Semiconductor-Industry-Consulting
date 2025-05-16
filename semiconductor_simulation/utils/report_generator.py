import os
import html
from datetime import datetime

def generate_html_report(simulation_results: dict, scenario_name: str, start_year: int, end_year: int, output_dir: str, timestamp: str, plot_filenames: list = None):
    """
    Generates an HTML report from the simulation results.

    Args:
        simulation_results (dict): The dictionary containing simulation results.
        scenario_name (str): Name of the scenario.
        start_year (int): Simulation start year.
        end_year (int): Simulation end year.
        output_dir (str): Directory to save the report.
        timestamp (str): Timestamp string for the report filename.
        plot_filenames (list, optional): List of plot filenames to embed. Defaults to an empty list.
    """
    if plot_filenames is None:
        plot_filenames = []
    
    report_filename = os.path.join(output_dir, f"{scenario_name}_report_{timestamp}.html")

    # HTML structure from previous correct version, with plot section added
    html_content = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Simulation Report: {html.escape(scenario_name)}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; color: #333; }}
        .container {{ background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #4CAF50; margin-top: 30px; }}
        h3 {{ color: #555; margin-top: 20px; }}
        h4 {{ color: #666; margin-top: 15px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f0f0f0; }}
        .code {{ background-color: #eee; padding: 2px 6px; border-radius: 4px; font-family: monospace; }}
        .parameters ul {{ list-style-type: none; padding-left: 0; }}
        .parameters li {{ background-color: #e9e9e9; margin-bottom: 5px; padding: 8px; border-radius: 4px; }}
        .parameters li strong {{ color: #333; }}
        .model-section {{ margin-bottom: 30px; border-left: 3px solid #4CAF50; padding-left: 15px; }}
        .plots {{ margin-top: 30px; }}
        .plot-container {{ margin-bottom: 20px; padding: 10px; background-color: #f9f9f9; border-radius: 4px; }}
        .plot-image {{ max-width: 100%; height: auto; border: 1px solid #ddd; margin-top: 10px; display: block; margin-left: auto; margin-right: auto; }}
    </style>
</head>
<body>
    <div class=\"container\">
        <h1>Simulation Report: {html.escape(scenario_name)}</h1>
        <p><strong>Run Timestamp:</strong> {html.escape(timestamp)}</p>
        <p><strong>Simulation Period:</strong> {start_year} - {end_year}</p>

        <div class=\"parameters\">
            <h2>Global Parameters</h2>
            {_generate_global_params_html(simulation_results.get("global_parameters", {}))}
        </div>

        <div class=\"model-results\">
            <h2>Model Results Summary</h2>
            {_generate_model_results_html(simulation_results.get("model_trajectories", {}))}
        </div>

        <div class=\"plots\">
            <h2>Visualizations</h2>
            {_generate_plots_html(plot_filenames)} 
        </div>

    </div>
</body>
</html>
"""

    try:
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML report generated: {report_filename}")
    except IOError as e:
        print(f"Error writing HTML report to {report_filename}: {e}")

def _generate_global_params_html(global_params: dict) -> str:
    if not global_params:
        return "<p>No global parameters found.</p>"
    items_html = ""
    for key, value in global_params.items():
        items_html += f"<li><strong>{html.escape(str(key))}:</strong> {html.escape(str(value))}</li>"
    return f"<ul>{items_html}</ul>"

def _generate_model_results_html(model_trajectories: dict) -> str:
    if not model_trajectories:
        return "<p>No model trajectory data found.</p>"
    
    content_html = ""
    for model_type, models_data in model_trajectories.items():
        if not models_data:
            continue
        content_html += f"<div class=\"model-section\">"
        content_html += f"<h3>{html.escape(model_type.replace('_', ' ').title())}</h3>"
        
        for model_id, trajectory in models_data.items():
            if not trajectory:
                content_html += f"<p>No data for {html.escape(model_id)}.</p>"
                continue

            content_html += f"<h4>{html.escape(model_id)}</h4>"
            
            initial_state = trajectory[0]
            final_state = trajectory[-1]
            
            table_html = "<table><thead><tr><th>Attribute</th><th>Initial Value ({html.escape(str(initial_state.get('year', 'N/A' )))})</th><th>Final Value ({html.escape(str(final_state.get('year', 'N/A' )))})</th></tr></thead><tbody>"
            
            all_keys = set(initial_state.keys()) | set(final_state.keys())
            if 'year' in all_keys:
                all_keys.remove('year')
            
            sorted_keys = sorted(list(all_keys))

            for attr in sorted_keys:
                initial_val = initial_state.get(attr, "N/A")
                final_val = final_state.get(attr, "N/A")
                # Simple check to avoid overly long string representations in table for now
                str_initial_val = str(initial_val)
                str_final_val = str(final_val)
                if len(str_initial_val) > 70: str_initial_val = str_initial_val[:67] + "..."
                if len(str_final_val) > 70: str_final_val = str_final_val[:67] + "..."
                table_html += f"<tr><td>{html.escape(str(attr))}</td><td>{html.escape(str_initial_val)}</td><td>{html.escape(str_final_val)}</td></tr>"
            
            table_html += "</tbody></table>"
            content_html += table_html
        content_html += "</div>"
        
    return content_html

def _generate_plots_html(plot_filenames: list) -> str:
    if not plot_filenames:
        return "<p>No plots were generated or provided for this report.</p>"
    
    items_html = ""
    for plot_file in plot_filenames:
        plot_name = html.escape(os.path.splitext(plot_file)[0].replace('_', ' ').title())
        # Ensure relative path for src if plots are in the same directory
        # The plot_file is already just the basename from main.py
        items_html += f'''
    <div class="plot-container">
        <h4>{plot_name}</h4>
        <img src="{html.escape(plot_file)}" alt="{plot_name}" class="plot-image">
    </div>
'''
    return items_html

if __name__ == '__main__':
    # Example usage (for testing purposes)
    mock_results = {
        "scenario_name": "Test HTML Scenario",
        "simulation_start_year": 2025,
        "simulation_end_year": 2030,
        "global_parameters": {
            "inflation_rate": 0.025,
            "trade_tension_factor": 0.2,
            "a_very_long_parameter_string_for_testing_wrapping_or_truncation_if_implemented": "This is a very long string value to see how it is handled in the HTML report just in case we decide to show it somewhere."
        },
        "model_trajectories": {
            "regions": {
                "USA": [
                    {"year": 2025, "gdp": 25.0e12, "semiconductor_engineer_count": 70000, "talent_notes": "Initial notes here."},
                    {"year": 2030, "gdp": 28.0e12, "semiconductor_engineer_count": 75000, "talent_notes": "Updated notes after simulation, potentially very long to test truncation if implemented in table cells. This note could be extremely verbose and detailed, covering all aspects of the talent pool evolution over the simulated period, including specific numbers, new training programs, and government initiatives. We need to ensure this does not break the table layout."}
                ]
            },
            "companies": {
                "CompA": [
                    {"year": 2025, "revenue": 150e9, "market_share": 0.20},
                    {"year": 2030, "revenue": 180e9, "market_share": 0.22}
                ]
            }
        }
    }
    mock_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Corrected mock_output_dir for __main__ to match expected structure from project
    # It should be semiconductor_simulation/results if running from project root, or just results if running utils/report_generator.py directly
    # For direct execution of this script, saving to a local 'results' is fine.
    mock_output_dir = "results" 
    if not os.path.exists(mock_output_dir):
        os.makedirs(mock_output_dir)

    # Example plot filenames for testing
    test_plot_filenames = [f"Test_HTML_Scenario_regions_USA_gdp_{mock_timestamp}.png", f"Test_HTML_Scenario_companies_CompA_revenue_{mock_timestamp}.png"]
    # Create dummy plot files for the __main__ example to work visually
    for pf in test_plot_filenames:
        try:
            # Simple placeholder for a plot image (e.g., a small transparent PNG as base64)
            # This avoids needing matplotlib for this test script if not already imported.
            # For a real test, one might generate actual dummy plots.
            dummy_plot_content = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=" # 1x1 transparent png
            import base64
            with open(os.path.join(mock_output_dir, pf), 'wb') as f:
                f.write(base64.b64decode(dummy_plot_content))
            print(f"Created dummy plot: {os.path.join(mock_output_dir, pf)}")
        except Exception as e:
            print(f"Could not create dummy plot {pf}: {e}")
            # Fallback to simple text file if base64 fails (e.g. import error)
            try:
                with open(os.path.join(mock_output_dir, pf), 'w') as f:
                    f.write("This is a dummy plot image file.")
            except IOError:
                pass 

    generate_html_report(
        simulation_results=mock_results,
        scenario_name=mock_results["scenario_name"],
        start_year=mock_results["simulation_start_year"],
        end_year=mock_results["simulation_end_year"],
        output_dir=mock_output_dir,
        timestamp=mock_timestamp,
        plot_filenames=test_plot_filenames
    )
    print(f"Mock report generated in {os.path.join(mock_output_dir, mock_results['scenario_name'] + '_report_' + mock_timestamp + '.html')}") 