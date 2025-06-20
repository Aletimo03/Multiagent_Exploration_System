import os
import statistics
from Constants import *
import pickle
from Plots import *

# Determine project root (two levels up from this file)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

types_of_search = ["systematic", "local", "annealing forward", "annealing reverse", "penalty"]
types_of_search_dict = {f"{search_type} search": idx for idx, search_type in enumerate(types_of_search)}

coverages = [[] for _ in range(len(types_of_search))]
exploration_levels = [[] for _ in range(len(types_of_search))]
times = [[] for _ in range(len(types_of_search))]

for type_of_search, type_value in types_of_search_dict.items():
    for j in range(NUM_OF_SIMULATIONS):
        base_path = os.path.join(project_root, "Experiment results", "experiment2", type_of_search, str(j))
        cov_path = os.path.join(base_path, "coverages.p")
        time_path = os.path.join(base_path, "time_elapsed.p")
        expl_path = os.path.join(base_path, "exploration_levels.p")

        # Debug prints to check paths and existence
        print(f"Loading coverage from: {cov_path} -> Exists: {os.path.exists(cov_path)}")
        print(f"Loading time from: {time_path} -> Exists: {os.path.exists(time_path)}")
        print(f"Loading exploration from: {expl_path} -> Exists: {os.path.exists(expl_path)}")

        with open(cov_path, "rb") as f_cov, open(time_path, "rb") as f_time, open(expl_path, "rb") as f_expl:
            coverages[type_value].append(pickle.load(f_cov))
            times[type_value].append(pickle.load(f_time))
            exploration_levels[type_value].append(pickle.load(f_expl))

times_avg = [statistics.mean(time) for time in times]

for type_of_search in types_of_search_dict.keys():
    avg_dir = os.path.join(project_root, "Experiment results", "experiment2", type_of_search, "average")
    os.makedirs(avg_dir, exist_ok=True)
    avg_time_path = os.path.join(project_root, "Experiment results", "experiment2", type_of_search, "average_time_elapsed.txt")
    with open(avg_time_path, "w") as f:
        f.write(str(times_avg[types_of_search_dict[type_of_search]]) + "\n")

final_coverages = [[0 for _ in range(len(coverages[0]))] for _ in range(len(coverages))]
final_explorations = [[0 for _ in range(len(exploration_levels[0]))] for _ in range(len(exploration_levels))]

for i in range(len(coverages)):
    for j in range(len(coverages[i])):
        final_coverages[i][j] = coverages[i][j][-1]
        final_explorations[i][j] = exploration_levels[i][j][-1]

mean_covs = [statistics.mean(final_coverage) for final_coverage in final_coverages]
max_covs = [max(final_coverage) for final_coverage in final_coverages]
min_covs = [min(final_coverage) for final_coverage in final_coverages]
std_devs_covs = [statistics.stdev(final_coverage) for final_coverage in final_coverages]

for type_of_search in types_of_search_dict.keys():
    avg_dir = os.path.join(project_root, "Experiment results", "experiment2", type_of_search, "average")
    os.makedirs(avg_dir, exist_ok=True)
    idx = types_of_search_dict[type_of_search]
    with open(os.path.join(avg_dir, "mean_coverage.txt"), "w") as f:
        f.write(str(mean_covs[idx]) + "\n")
    with open(os.path.join(avg_dir, "max_coverage.txt"), "w") as f:
        f.write(str(max_covs[idx]) + "\n")
    with open(os.path.join(avg_dir, "min_coverage.txt"), "w") as f:
        f.write(str(min_covs[idx]) + "\n")
    with open(os.path.join(avg_dir, "std_dev_coverage.txt"), "w") as f:
        f.write(str(std_devs_covs[idx]) + "\n")

mean_expls = [statistics.mean(final_exploration) for final_exploration in final_explorations]
max_expls = [max(final_exploration) for final_exploration in final_explorations]
min_expls = [min(final_exploration) for final_exploration in final_explorations]
std_devs_expls = [statistics.stdev(final_exploration) for final_exploration in final_explorations]

for type_of_search in types_of_search_dict.keys():
    avg_dir = os.path.join(project_root, "Experiment results", "experiment2", type_of_search, "average")
    idx = types_of_search_dict[type_of_search]
    with open(os.path.join(avg_dir, "mean_exploration.txt"), "w") as f:
        f.write(str(mean_expls[idx]) + "\n")
    with open(os.path.join(avg_dir, "max_exploration.txt"), "w") as f:
        f.write(str(max_expls[idx]) + "\n")
    with open(os.path.join(avg_dir, "min_exploration.txt"), "w") as f:
        f.write(str(min_expls[idx]) + "\n")
    with open(os.path.join(avg_dir, "std_dev_exploration.txt"), "w") as f:
        f.write(str(std_devs_expls[idx]) + "\n")

average_coverages = [[0 for _ in range(NUM_OF_ITERATIONS + 1)] for _ in range(len(types_of_search))]
average_explorations = [[0 for _ in range(NUM_OF_ITERATIONS + 1)] for _ in range(len(types_of_search))]

for i in range(len(types_of_search)):
    for k in range(NUM_OF_ITERATIONS + 1):
        for j in range(NUM_OF_SIMULATIONS):
            average_coverages[i][k] += coverages[i][j][k]
            average_explorations[i][k] += exploration_levels[i][j][k]
        average_coverages[i][k] /= NUM_OF_SIMULATIONS
        average_explorations[i][k] /= NUM_OF_SIMULATIONS

for type_of_search in types_of_search_dict.keys():
    idx = types_of_search_dict[type_of_search]
    plot_coverage(
        average_coverages[idx],
        times_avg[idx],
        type_of_search.replace(" search", ""),
        None,
        "average",
        None,
        None,
    )
    plot_exploration(
        average_explorations[idx],
        times_avg[idx],
        type_of_search.replace(" search", ""),
        None,
        "average",
        None,
    )

plot_coverages_comparison(average_coverages, types_of_search)
plot_exploration_comparison(average_explorations, types_of_search)
