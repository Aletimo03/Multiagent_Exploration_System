import os
import pickle
from Constants import *
import numpy as np
from Plots import plot_coverages_comparison, plot_exploration_comparison
from scipy.signal import savgol_filter


# Toggle smoothing on/off
SMOOTH_CURVES = True

def smooth_curve(data, window_length=11, polyorder=3):
    """
    Smooths the data using the Savitzky-Golay filter.
    """
    if len(data) < window_length:
        return data
    return savgol_filter(data, window_length=window_length, polyorder=polyorder).tolist()


# Define the configurations with descriptive labels and folder paths
configs = {
    "low variability": "custom prob True/low variability",
    "medium variability": "custom prob False",
    "high variability": "custom prob True/high variability"
}

# Prepare containers
coverages = {label: [] for label in configs}
exploration_levels = {label: [] for label in configs}

# Project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
print(f"Project root resolved to: {project_root}\n")

# Load data
for label, rel_path in configs.items():
    print(f"Processing: {label} ({rel_path})")

    for j in range(30):  # or NUM_OF_SIMULATIONS
        base_path = os.path.join(project_root, f"Experiment results/experiment3/{rel_path}/{j}")
        cov_path = os.path.join(base_path, "coverages.p")
        expl_path = os.path.join(base_path, "exploration_levels.p")

        print(f"  Simulation {j}:")
        print(f"    Coverage file exists: {os.path.exists(cov_path)}")
        print(f"    Exploration file exists: {os.path.exists(expl_path)}")

        if not os.path.exists(cov_path):
            raise FileNotFoundError(f"Missing coverage file: {cov_path}")
        if not os.path.exists(expl_path):
            raise FileNotFoundError(f"Missing exploration file: {expl_path}")

        with open(cov_path, "rb") as f_cov, open(expl_path, "rb") as f_expl:
            coverage_data = pickle.load(f_cov)
            exploration_data = pickle.load(f_expl)
            coverages[label].append(coverage_data)
            exploration_levels[label].append(exploration_data)

    print(f"Total simulations loaded for {label}: {len(coverages[label])}\n")

# Compute averages
average_coverages = {label: [0] * (NUM_OF_ITERATIONS + 1) for label in configs}
average_explorations = {label: [0] * (NUM_OF_ITERATIONS + 1) for label in configs}

for label in configs:
    num_sims = len(coverages[label])
    print(f"Averaging data for {label} with {num_sims} simulations")

    for k in range(NUM_OF_ITERATIONS + 1):
        total_cov = total_expl = count_cov = count_expl = 0

        for j in range(num_sims):
            cov = coverages[label][j]
            expl = exploration_levels[label][j]

            if k < len(cov):
                total_cov += cov[k]
                count_cov += 1
            if k < len(expl):
                total_expl += expl[k]
                count_expl += 1

        average_coverages[label][k] = total_cov / count_cov if count_cov else 0
        average_explorations[label][k] = total_expl / count_expl if count_expl else 0

print("\nAveraging complete.\n")

# Log statistics for final iteration
print("\n===== Final Statistics =====")
for label in configs:
    final_covs = [cov[-1] for cov in coverages[label] if len(cov) > 0]
    final_expls = [expl[-1] for expl in exploration_levels[label] if len(expl) > 0]

    cov_avg = np.mean(final_covs)
    cov_min = np.min(final_covs)
    cov_max = np.max(final_covs)
    cov_std = np.std(final_covs)

    expl_avg = np.mean(final_expls)
    expl_min = np.min(final_expls)
    expl_max = np.max(final_expls)
    expl_std = np.std(final_expls)

    print(f"\n📊 {label.upper()}:")
    print(f"  Coverage   -> avg: {cov_avg:.2f}, min: {cov_min:.2f}, max: {cov_max:.2f}, std: {cov_std:.3f}")
    print(f"  Exploration-> avg: {expl_avg:.2f}, min: {expl_min:.2f}, max: {expl_max:.2f}, std: {expl_std:.3f}")

# Plot results
output_path = os.path.join(project_root, "Experiment results/experiment3/")
print(f"\nPlotting results to: {output_path}")

# Use smoothed or raw data depending on flag
if SMOOTH_CURVES:
    print("Smoothing enabled: applying Savitzky-Golay filter.")
    plotted_coverages = {
        label: smooth_curve(average_coverages[label], window_length=15, polyorder=3)
        for label in configs
    }
    plotted_explorations = {
        label: smooth_curve(average_explorations[label], window_length=15, polyorder=3)
        for label in configs
    }
else:
    print("Smoothing disabled: using raw averaged data.")
    plotted_coverages = average_coverages
    plotted_explorations = average_explorations

# Plot results
plot_coverages_comparison(
    list(plotted_coverages.values()),
    list(plotted_coverages.keys()),
    path=output_path
)

plot_exploration_comparison(
    list(plotted_explorations.values()),
    list(plotted_explorations.keys()),
    path=output_path
)
