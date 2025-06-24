import os
import pickle
import statistics
from Constants import *
from Plots import plot_coverage, plot_coverages_comparison, plot_exploration_comparison

# Define types of search
types_of_search = ["systematic", "local", "annealing forward", "annealing reverse", "penalty"]

# Prepare containers for loaded data
coverages = {search_type: [] for search_type in types_of_search}
exploration_levels = {search_type: [] for search_type in types_of_search}

# Determine project root based on the script location
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
print(f"Project root resolved to: {project_root}\n")

# Load data from files
for search_type in types_of_search:
    print(f"Processing {search_type} search:")
    for j in range(NUM_OF_SIMULATIONS):
        base_path = os.path.join(project_root, f"Experiment results/experiment2/{search_type} search/{j}")
        cov_path = os.path.join(base_path, "coverages.p")
        expl_path = os.path.join(base_path, "exploration_levels.p")

        print(f"  Simulation {j}:")
        print(f"    Base path: {base_path}")
        print(f"    Coverage file exists: {os.path.exists(cov_path)}")
        print(f"    Exploration file exists: {os.path.exists(expl_path)}")

        if not os.path.exists(cov_path):
            raise FileNotFoundError(f"Missing coverage file: {cov_path}")
        if not os.path.exists(expl_path):
            raise FileNotFoundError(f"Missing exploration file: {expl_path}")

        with open(cov_path, "rb") as f_cov, open(expl_path, "rb") as f_expl:
            coverage_data = pickle.load(f_cov)
            exploration_data = pickle.load(f_expl)
            print(f"    Loaded coverage data length: {len(coverage_data)}")
            print(f"    Loaded exploration data length: {len(exploration_data)}")
            coverages[search_type].append(coverage_data)
            exploration_levels[search_type].append(exploration_data)

    print(f"Total simulations loaded for {search_type} search: {len(coverages[search_type])}\n")

# Initialize average containers
average_coverages = {search_type: [0] * (NUM_OF_ITERATIONS + 1) for search_type in types_of_search}
average_explorations = {search_type: [0] * (NUM_OF_ITERATIONS + 1) for search_type in types_of_search}

# Compute averages across simulations, adapt to actual loaded data length
for search_type in types_of_search:
    num_sims = len(coverages[search_type])
    print(f"Averaging data for {search_type} search with {num_sims} simulations")

    for k in range(NUM_OF_ITERATIONS + 1):
        total_cov = 0
        total_expl = 0
        count_cov = 0
        count_expl = 0

        for j in range(num_sims):
            cov_len = len(coverages[search_type][j])
            expl_len = len(exploration_levels[search_type][j])

            if k < cov_len:
                total_cov += coverages[search_type][j][k]
                count_cov += 1
            else:
                print(f"    Warning: coverage index {k} out of range for simulation {j} (length {cov_len})")

            if k < expl_len:
                total_expl += exploration_levels[search_type][j][k]
                count_expl += 1
            else:
                print(f"    Warning: exploration index {k} out of range for simulation {j} (length {expl_len})")

        average_coverages[search_type][k] = (total_cov / count_cov) if count_cov > 0 else 0
        average_explorations[search_type][k] = (total_expl / count_expl) if count_expl > 0 else 0

print("\nAveraging complete.\n")


# Plot results
output_path = os.path.join(project_root, "Experiment results/experiment2/")
print(f"Plotting results to: {output_path}")

plot_coverages_comparison(
    average_coverages.values(),
    ["systematic", "local", "annealing forward", "annealing reverse", "penalty"],
    path=output_path
)

plot_exploration_comparison(
    average_explorations.values(),
    ["systematic", "local", "annealing forward", "annealing reverse", "penalty"],
    path=output_path
)

