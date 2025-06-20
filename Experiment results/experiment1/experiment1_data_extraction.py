import os
import pickle
from matplotlib import pyplot as plt
import statistics
from Constants import NUM_OF_SIMULATIONS, NUM_OF_ITERATIONS

# Resolve project root relative to this script file
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
print(f"Project root resolved to: {project_root}\n")

# Initialize data containers
coverages = {True: {True: [], False: []}, False: {True: [], False: []}}
explorations = {True: [], False: []}

# Load all data
for expl in [True, False]:
    for bs in [True, False]:
        for i in range(NUM_OF_SIMULATIONS):
            base_path = os.path.join(project_root, f"Experiment results/experiment1/expl {expl}/BS {bs}/{i}")
            cov_path = os.path.join(base_path, "coverages.p")
            expl_path = os.path.join(base_path, "exploration_levels.p")

            print(f"Loading coverage from: {cov_path}")
            with open(cov_path, 'rb') as f_cov:
                coverages[expl][bs].append(pickle.load(f_cov))

            if expl:
                print(f"Loading exploration from: {expl_path}")
                with open(expl_path, 'rb') as f_expl:
                    explorations[bs].append(pickle.load(f_expl))

# Compute final statistics
final_cov = {True: {True: [0]*NUM_OF_SIMULATIONS, False: [0]*NUM_OF_SIMULATIONS},
             False: {True: [0]*NUM_OF_SIMULATIONS, False: [0]*NUM_OF_SIMULATIONS}}
final_expl = {True: [0]*NUM_OF_SIMULATIONS, False: [0]*NUM_OF_SIMULATIONS}

for expl in [True, False]:
    for bs in [True, False]:
        for i in range(NUM_OF_SIMULATIONS):
            final_cov[expl][bs][i] = coverages[expl][bs][i][-1]
            if expl:
                final_expl[bs][i] = explorations[bs][i][-1]

# Write final statistics to files
for expl in [True, False]:
    for bs in [True, False]:
        stats_path_cov = os.path.join(project_root, f"Experiment results/experiment1/expl {expl}/BS {bs}/final_coverage_statistics.txt")
        with open(stats_path_cov, 'w') as f:
            output = (f"max: {max(final_cov[expl][bs])} "
                      f"min: {min(final_cov[expl][bs])} "
                      f"avg: {statistics.mean(final_cov[expl][bs])} "
                      f"std_dev: {statistics.stdev(final_cov[expl][bs])} ")
            f.write(output)

        if expl:
            stats_path_expl = os.path.join(project_root, f"Experiment results/experiment1/expl {expl}/BS {bs}/final_exploration_statistics.txt")
            with open(stats_path_expl, 'w') as f:
                output = (f"max: {max(final_expl[bs])} "
                          f"min: {min(final_expl[bs])} "
                          f"avg: {statistics.mean(final_expl[bs])} "
                          f"std_dev: {statistics.stdev(final_expl[bs])}")
                f.write(output)

# Compute average coverage and exploration over iterations
avg_cov = {True: {True: [0]*NUM_OF_ITERATIONS, False: [0]*NUM_OF_ITERATIONS},
           False: {True: [0]*NUM_OF_ITERATIONS, False: [0]*NUM_OF_ITERATIONS}}
avg_expl = {True: [0]*NUM_OF_ITERATIONS, False: [0]*NUM_OF_ITERATIONS}

min_starting_coverages = []

for expl in [True, False]:
    for bs in [True, False]:
        for j in range(NUM_OF_ITERATIONS):
            avg_cov_iter = 0
            avg_expl_iter = 0

            for i in range(NUM_OF_SIMULATIONS):
                avg_cov_iter += coverages[expl][bs][i][j]
                if expl:
                    avg_expl_iter += explorations[bs][i][j]

            avg_cov_iter /= NUM_OF_SIMULATIONS
            avg_cov[expl][bs][j] = avg_cov_iter
            if j == 0:
                min_starting_coverages.append(avg_cov_iter)
            if expl:
                avg_expl_iter /= NUM_OF_SIMULATIONS
                avg_expl[bs][j] = avg_expl_iter

min_starting_cov = min(min_starting_coverages)

# Plot coverage comparison
fig, ax = plt.subplots(1, 2, figsize=(10, 5), constrained_layout=True)
ax[0].set_xlabel("Iteration")
ax[0].set_ylabel("Coverage")
ax[0].set_ylim(min_starting_cov, 1)
ax[0].plot(range(len(avg_cov[True][True])), avg_cov[True][True], label="with exploration")
ax[0].plot(range(len(avg_cov[False][True])), avg_cov[False][True], label="without exploration")
ax[0].legend(loc='lower right')
ax[0].set_title("Coverage comparison with Base Stations")

ax[1].set_xlabel("Iteration")
ax[1].set_ylabel("Coverage")
ax[1].set_ylim(min_starting_cov, 1)
ax[1].plot(range(len(avg_cov[True][False])), avg_cov[True][False], label="with exploration")
ax[1].plot(range(len(avg_cov[False][False])), avg_cov[False][False], label="without exploration")
ax[1].legend(loc='lower right')
ax[1].set_title("Coverage comparison without Base Stations")

fig_path_cov = os.path.join(project_root, "Experiment results/experiment1/coverage_comparison.png")
fig.savefig(fig_path_cov, bbox_inches='tight')
print(f"Saved coverage comparison plot at {fig_path_cov}")

# Plot exploration comparison
fig, ax = plt.subplots()
ax.set_xlabel("Iteration")
ax.set_ylabel("Exploration level")
ax.plot(avg_expl[True], label="with BS")
ax.plot(avg_expl[False], label="without BS")
ax.legend(loc='lower right')
ax.set_title("Exploration comparison")

fig_path_expl = os.path.join(project_root, "Experiment results/experiment1/exploration_comparison.png")
fig.savefig(fig_path_expl, bbox_inches='tight')
print(f"Saved exploration comparison plot at {fig_path_expl}")
