import os
import pickle
import statistics
from Constants import *
from Plots import plot_coverage, plot_coverages_comparison, plot_exploration_comparison

# Define your custom probabilities to process
custom_probs = [False, True]

# Prepare containers for loaded data
coverages = {True: [], False: []}
exploration_levels = {True: [], False: []}

# Determine project root based on the script location
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
print(f"Project root resolved to: {project_root}\n")

# Load data from files
for prob in custom_probs:
    print(f"Processing prob = {prob}")
    for j in range(NUM_OF_SIMULATIONS):
        base_path = os.path.join(project_root, f"Experiment results/experiment3/custom prob {prob}/{j}")
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
            coverages[prob].append(coverage_data)
            exploration_levels[prob].append(exploration_data)

    print(f"Total simulations loaded for prob={prob}: {len(coverages[prob])}\n")

# Initialize average containers
average_coverages = {True: [0] * (NUM_OF_ITERATIONS + 1), False: [0] * (NUM_OF_ITERATIONS + 1)}
average_explorations = {True: [0] * (NUM_OF_ITERATIONS + 1), False: [0] * (NUM_OF_ITERATIONS + 1)}

# Compute averages across simulations, adapt to actual loaded data length
for prob in custom_probs:
    num_sims = len(coverages[prob])
    print(f"Averaging data for prob={prob} with {num_sims} simulations")

    for k in range(NUM_OF_ITERATIONS + 1):
        total_cov = 0
        total_expl = 0
        count_cov = 0
        count_expl = 0

        for j in range(num_sims):
            cov_len = len(coverages[prob][j])
            expl_len = len(exploration_levels[prob][j])

            if k < cov_len:
                total_cov += coverages[prob][j][k]
                count_cov += 1
            else:
                print(f"    Warning: coverage index {k} out of range for simulation {j} (length {cov_len})")

            if k < expl_len:
                total_expl += exploration_levels[prob][j][k]
                count_expl += 1
            else:
                print(f"    Warning: exploration index {k} out of range for simulation {j} (length {expl_len})")

        average_coverages[prob][k] = (total_cov / count_cov) if count_cov > 0 else 0
        average_explorations[prob][k] = (total_expl / count_expl) if count_expl > 0 else 0

print("\nAveraging complete.\n")

# Plot results
output_path = os.path.join(project_root, "Experiment results/experiment3/")
print(f"Plotting results to: {output_path}")

plot_coverages_comparison(
    average_coverages.values(),
    ['high variability', 'low variability'],
    path=output_path
)

plot_exploration_comparison(
    average_explorations.values(),
    ['high variability', 'low variability'],
    path=output_path
)
