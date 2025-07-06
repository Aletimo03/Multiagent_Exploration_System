import os
import pickle
import numpy as np
from Constants import *
from Plots import plot_coverages_comparison, plot_exploration_comparison
from scipy.signal import savgol_filter

def smooth_curve(data, window_length=11, polyorder=3):
    """
    Smooths the data using the Savitzky-Golay filter.
    """
    if len(data) < window_length:
        return data
    return savgol_filter(data, window_length=window_length, polyorder=polyorder).tolist()


USE_SMOOTHING = True

# Define the types of search algorithms
types_of_search = ["systematic", "local", "annealing forward", "annealing reverse", "penalty"]

# Initialize containers for results
coverages = {t: [] for t in types_of_search}
exploration_levels = {t: [] for t in types_of_search}
times_elapsed = {t: [] for t in types_of_search}

# Resolve project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
print(f"Project root resolved to: {project_root}\n")

# Load all data
for search_type in types_of_search:
    print(f"Processing '{search_type}' search:")

    for j in range(30):  # or NUM_OF_SIMULATIONS
        base_path = os.path.join(project_root, f"Experiment results/experiment2/{search_type} search/{j}")
        cov_path = os.path.join(base_path, "coverages.p")
        expl_path = os.path.join(base_path, "exploration_levels.p")
        time_path = os.path.join(base_path, "time_elapsed.p")

        if not os.path.exists(cov_path):
            raise FileNotFoundError(f"Missing file: {cov_path}")
        if not os.path.exists(expl_path):
            raise FileNotFoundError(f"Missing file: {expl_path}")
        if not os.path.exists(time_path):
            raise FileNotFoundError(f"Missing file: {time_path}")

        with open(cov_path, "rb") as f_cov, \
             open(expl_path, "rb") as f_expl, \
             open(time_path, "rb") as f_time:
            coverages[search_type].append(pickle.load(f_cov))
            exploration_levels[search_type].append(pickle.load(f_expl))
            times_elapsed[search_type].append(pickle.load(f_time))

    print(f"Loaded {len(coverages[search_type])} simulations for '{search_type}' search.\n")

# Compute averages
average_coverages = {t: [0] * (NUM_OF_ITERATIONS + 1) for t in types_of_search}
average_explorations = {t: [0] * (NUM_OF_ITERATIONS + 1) for t in types_of_search}

for t in types_of_search:
    for k in range(NUM_OF_ITERATIONS + 1):
        cov_values = [cov[k] for cov in coverages[t] if len(cov) > k]
        expl_values = [expl[k] for expl in exploration_levels[t] if len(expl) > k]
        average_coverages[t][k] = np.mean(cov_values) if cov_values else 0
        average_explorations[t][k] = np.mean(expl_values) if expl_values else 0

print("Averaging complete.\n")

# Final statistics (last iteration only)
print("===== Final Statistics (Last Iteration) =====")
for t in types_of_search:
    final_covs = [cov[-1] for cov in coverages[t] if cov]
    final_expls = [expl[-1] for expl in exploration_levels[t] if expl]
    times = times_elapsed[t]

    if final_covs and final_expls and times:
        cov_mean, cov_min, cov_max, cov_std = np.mean(final_covs), np.min(final_covs), np.max(final_covs), np.std(final_covs)
        expl_mean, expl_min, expl_max, expl_std = np.mean(final_expls), np.min(final_expls), np.max(final_expls), np.std(final_expls)
        time_mean = np.mean(times)

        print(f"\n{t.upper()}:")
        print(f"  Coverage     → mean: {cov_mean:.2f}, min: {cov_min:.2f}, max: {cov_max:.2f}, std: {cov_std:.3f}")
        print(f"  Exploration  → mean: {expl_mean:.2f}, min: {expl_min:.2f}, max: {expl_max:.2f}, std: {expl_std:.3f}")
        print(f"  Time Elapsed → average: {time_mean:.2f} seconds")
    else:
        print(f"\n{t.upper()}: No data available for statistics.")

# Plotting
output_path = os.path.join(project_root, "Experiment results/experiment2/")
print(f"\nSaving plots to: {output_path}")

if USE_SMOOTHING:
    smoothed_coverages = {t: smooth_curve(v, window_length=15, polyorder=3) for t, v in average_coverages.items()}
    smoothed_explorations = {t: smooth_curve(v, window_length=15, polyorder=3) for t, v in average_explorations.items()}
else:
    smoothed_coverages = average_coverages
    smoothed_explorations = average_explorations

# Plot using smoothed data
plot_coverages_comparison(
    list(smoothed_coverages.values()),
    list(smoothed_coverages.keys()),
    path=output_path
)

plot_exploration_comparison(
    list(smoothed_explorations.values()),
    list(smoothed_explorations.keys()),
    path=output_path
)
