import os
import html
from datetime import datetime

def generate_html_report(simulation_results: dict, scenario_name: str, start_year: int, end_year: int, output_dir: str, timestamp: str):
    """
    Generates an HTML report from the simulation results.

    Args:
        simulation_results (dict): The dictionary containing simulation results.
        scenario_name (str): Name of the scenario.
        start_year (int): Simulation start year.
        end_year (int): Simulation end year.
        output_dir (str): Directory to save the report.
        timestamp (str): Timestamp string for the report filename.
    """
    report_filename = os.path.join(output_dir, f"{scenario_name}_report_{timestamp}.html")

    # Basic HTML structure
    # Using html.escape for any dynamic string content inserted into the HTML
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
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f0f0f0; }}
        .code {{ background-color: #eee; padding: 2px 6px; border-radius: 4px; font-family: monospace; }}
        .parameters ul {{ list-style-type: none; padding-left: 0; }}
        .parameters li {{ background-color: #e9e9e9; margin-bottom: 5px; padding: 8px; border-radius: 4px; }}
        .parameters li strong {{ color: #333; }}
        .model-section {{ margin-bottom: 30px; border-left: 3px solid #4CAF50; padding-left: 15px; }}
        .plot-image {{ max-width: 100%; height: auto; border: 1px solid #ddd; margin-top: 10px; }}
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
            <!-- Placeholder for plots -->
            <p>Links to or embedded plots will be here.</p>
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
            
            # Get all unique keys from initial and final states, excluding 'year'
            all_keys = set(initial_state.keys()) | set(final_state.keys())
            if 'year' in all_keys: # Ensure 'year' is not treated as an attribute to compare
                all_keys.remove('year')
            
            sorted_keys = sorted(list(all_keys))

            for attr in sorted_keys:
                initial_val = initial_state.get(attr, "N/A")
                final_val = final_state.get(attr, "N/A")
                table_html += f"<tr><td>{html.escape(str(attr))}</td><td>{html.escape(str(initial_val))}</td><td>{html.escape(str(final_val))}</td></tr>"
            
            table_html += "</tbody></table>"
            content_html += table_html
        content_html += "</div>"
        
    return content_html

if __name__ == '__main__':
    # Example usage (for testing purposes)
    mock_results = {
        "scenario_name": "Test HTML Scenario",
        "simulation_start_year": 2025,
        "simulation_end_year": 2030,
        "global_parameters": {
            "inflation_rate": 0.025,
            "trade_tension_factor": 0.2
        },
        "model_trajectories": {
            "regions": {
                "USA": [
                    {"year": 2025, "gdp": 25.0e12, "semiconductor_engineer_count": 70000},
                    {"year": 2030, "gdp": 28.0e12, "semiconductor_engineer_count": 75000}
                ]
            },
            "companies": {
                "CompA": [
                    {"year": 2025, "revenue": 150e9, "market_share": 0.20},
                    {"year": 2030, "revenue": 180e9, "market_share": 0.22}
                ]
            }
        },
        "final_state": { # Optional: could be derived or explicitly stored
            "regions": {
                "USA": {"gdp": 28.0e12, "semiconductor_engineer_count": 75000, "talent_availability": "medium"}
            },
            "companies": {
                "CompA": {"revenue": 180e9, "market_share": 0.22}
            }
        }
    }
    mock_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    mock_output_dir = "results"
    if not os.path.exists(mock_output_dir):
        os.makedirs(mock_output_dir)

    generate_html_report(
        simulation_results=mock_results,
        scenario_name=mock_results["scenario_name"],
        start_year=mock_results["simulation_start_year"],
        end_year=mock_results["simulation_end_year"],
        output_dir=mock_output_dir,
        timestamp=mock_timestamp
    )
    print(f"Mock report generated in {mock_output_dir}/") 