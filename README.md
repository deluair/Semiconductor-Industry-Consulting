# Semiconductor Industry Strategic Foresight Simulation (2025-2040)

## 1. Project Overview

This project, "Comprehensive Simulation Prompt: Semiconductor Industry Consulting (2025-2040)," aims to create a dynamic simulation environment for strategic foresight in the global semiconductor industry. It models various entities (regions, companies, technology nodes, end markets, policies) and their interactions over a simulated period from 2025 to 2040.

The simulation allows for the exploration of different scenarios, such as the impact of geopolitical events (e.g., US CHIPS Act), technological advancements, and market shifts. The goal is to provide a tool for consultants and strategists to understand potential future states of the industry.

## 2. Project Structure

The project is organized into the `semiconductor_simulation` package and a main execution script:

```
.
├── main.py                     # Main script to run simulations
├── semiconductor_simulation/
│   ├── core/                   # Core simulation engine (SimulationManager, BaseModel, BaseModule)
│   │   ├── __init__.py
│   │   ├── base_model.py
│   │   ├── base_module.py
│   │   └── simulation_manager.py
│   ├── data/                   # (Initially planned, data currently loaded from config/)
│   ├── models/                 # Definitions for simulation entities
│   │   ├── __init__.py
│   │   ├── company.py
│   │   ├── end_market.py
│   │   ├── policy.py
│   │   ├── region.py
│   │   └── technology_node.py
│   ├── modules/                # Simulation modules for different aspects (geopolitics, capacity)
│   │   ├── __init__.py
│   │   ├── capacity_demand_module.py
│   │   ├── consulting_market_module.py
│   │   ├── geopolitical_module.py
│   │   ├── industry_structure_module.py
│   │   ├── national_ecosystem_module.py
│   │   └── tech_evolution_module.py
│   ├── utils/                  # Utility functions (data loading, plotting, reporting)
│   │   ├── __init__.py
│   │   ├── data_loader.py
│   │   ├── plotter.py
│   │   └── report_generator.py
│   └── __init__.py
├── config/
│   ├── base_data.yaml          # Base configuration data (e.g., model lifespans)
│   └── scenarios/
│       └── test_scenario.yaml  # Example scenario definition
├── results/                    # Output directory for simulation results, plots, and reports
│   └── (generated files...)
└── README.md                   # This file
```

## 3. Setup and Installation

1.  **Prerequisites:**
    *   Python 3.x (developed with Python 3.10+, but should be compatible with recent versions).
    *   `pip` for installing dependencies.

2.  **Dependencies:**
    The primary external dependency used for plotting is `matplotlib`. Other operations use standard Python libraries (`os`, `yaml`, `datetime`, `argparse`, `html`, `collections`).
    Install `matplotlib` and `PyYAML` (for YAML handling by `data_loader.py`):
    ```bash
    pip install matplotlib PyYAML
    ```

3.  **Clone the Repository (if applicable):**
    If you have this project from a Git repository:
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

## 4. Running the Simulation

The simulation is run using `main.py` from the root of the project directory.

```bash
python main.py --scenario <scenario_name>
```

*   `--scenario <scenario_name>`: Specifies the name of the scenario YAML file (without the `.yaml` extension) located in `config/scenarios/`.
    *   If omitted, it defaults to `test_scenario`.

**Example:**
```bash
python main.py --scenario test_scenario
```
or simply:
```bash
python main.py
```

The `main.py` script will:
1.  Bootstrap default configuration files (`config/base_data.yaml` and `config/scenarios/test_scenario.yaml`) if they don't exist.
2.  Load the specified scenario.
3.  Initialize the `SimulationManager`.
4.  Register and initialize simulation modules.
5.  Run the simulation year by year.
6.  Save the results.
7.  Generate plots.
8.  Generate an HTML report.

## 5. Configuration

*   **Scenario Files:** Located in `config/scenarios/`. These YAML files define:
    *   `scenario_name`, `simulation_start_year`, `simulation_end_year`.
    *   `global_parameters`: Global variables affecting the simulation.
    *   `models_initial_state`: Initial attributes for all model instances (regions, companies, technology nodes, end markets, policies). Each model instance must have a `model_id`, `name`, and an `initial_attributes` dictionary containing all its specific properties.

*   **Base Data:** `config/base_data.yaml` can store other baseline parameters not specific to a single scenario. Currently, it's used for example `model_lifespans`.

The `DEFAULT_TEST_SCENARIO_DATA` in `main.py` provides a template for the structure of `test_scenario.yaml`.

## 6. Outputs

All outputs are saved in the `results/` directory, timestamped to avoid overwriting:

*   **Raw Yearly Results YAML:** `results/<scenario_name>_yearly_results_<timestamp>.yaml`
    *   Contains the state of all models for each year of the simulation. Structure: `{year: {category: [model_states]}}`.
*   **Transformed Trajectories YAML:** `results/<scenario_name>_trajectories_<timestamp>.yaml`
    *   A transformed version of the results, grouping states by model. Structure: `{category: {model_id: [{year: year, **attributes}]}}`. Useful for analysis.
*   **Plots (PNG):** `results/<scenario_name>_<plot_details>.png`
    *   Visualizations of specific attributes over time (e.g., GDP of regions, engineer count for a specific region).
*   **HTML Report:** `results/<scenario_name>_report_<timestamp>.html`
    *   A summary report of the simulation run, including global parameters, initial vs. final states of models, and embedded plots.

## 7. Key Components

*   **`BaseModel` (`core/base_model.py`):** Abstract base class for all simulation entities. Handles common attributes like `model_id`, `name`, `attributes`, and `history`.
*   **`BaseModule` (`core/base_module.py`):** Abstract base class for simulation modules. Defines the interface for modules to `initialize` and `execute_year_step`.
*   **`SimulationManager` (`core/simulation_manager.py`):** Orchestrates the simulation. Manages model instances, modules, simulation time, scenario loading, and results collection.
*   **Models (`models/`):**
    *   `RegionModel`: Represents geographical regions.
    *   `CompanyModel`: Represents companies (IDMs, Foundries, Fabless, etc.).
    *   `TechnologyNodeModel`: Represents semiconductor technology nodes (e.g., 3nm, 5nm).
    *   `EndMarketModel`: Represents end markets (e.g., Smartphones, Automotive).
    *   `PolicyModel`: Represents governmental policies.
*   **Modules (`modules/`):**
    *   `GeopoliticalModule`: Handles geopolitical factors.
    *   `CapacityDemandModule`: Manages supply and demand dynamics.
    *   `TechEvolutionModule`: Simulates technology advancements.
    *   `IndustryStructureModule`: Models changes in market structure.
    *   (Other modules like `ConsultingMarketModule`, `NationalEcosystemModule` are placeholders).
*   **Utilities (`utils/`):**
    *   `data_loader.py`: Loads YAML configuration files.
    *   `plotter.py`: Generates plots from simulation results using Matplotlib.
    *   `report_generator.py`: Creates an HTML summary report.

This README provides a starting point. It can be expanded with more details on specific model attributes, module logic, and advanced configuration options as the project evolves. 