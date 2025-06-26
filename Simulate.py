import os
import pickle
from concurrent.futures import ProcessPoolExecutor
from timeit import default_timer as timer

from Plots import plot_area, plot_coverage, plot_exploration
from Control_function import Control_function
from Sensor import Agent, Base_station
from Area import Area
from User import User
from Constants import *
from Control_function_config_DTO import Control_function_DTO as DTO


def goal_worker(args):
    """
    Worker function to calculate goal point for one agent.
    """
    agent, agents_snapshot, t, cf_params = args
    # cf_params: dict with parameters needed for cf method, avoiding passing full cf instance
    other_agents = [a for a in agents_snapshot if a.id != agent.id]
    goal = cf_params['cf'].find_goal_point_for_agent(agent, other_agents, t, print_expl_eval=False)
    return agent.id, goal


def simulate(type_of_search, expl_weight, num_of_iter, deserialize,
             use_expl, use_bs, experiment_id, use_custom_prob=False):
    """
    Run simulation with given parameters.
    """
    area = Area(AREA_WIDTH, AREA_LENGTH)

    # Create agents with increasing altitudes
    agents = [
        Agent(area, COMMUNICATION_RADIUS, TRANSMITTING_POWER,
              ALTITUDE + i * SENSOR_HEIGHT + MIN_VERTICAL_DISTANCE,
              deserialize)
        for i in range(N)
    ]

    base_stations = []
    if use_bs:
        quarter_w, quarter_l = area.width / 4, area.length / 4
        base_stations = [
            Base_station(area, COMMUNICATION_RADIUS, x, y, TYPE_OF_SCENARIO)
            for x, y in [
                (quarter_w, quarter_l),
                (quarter_w, 3 * quarter_l),
                (3 * quarter_w, quarter_l),
                (3 * quarter_w, 3 * quarter_l),
            ]
        ]

    users = [User(area, DESIRED_COVERAGE_LEVEL, deserialize) for _ in range(M)]

    user_trajectories = [
        user.simulate_trajectory_ct(steps=NUM_OF_ITERATIONS, area_width=area.width,
                                    area_length=area.length, deserialize=deserialize)
        for user in users
    ]

    coverage_levels = []
    exploration_levels = []
    prob_matrix_history = []

    dto = DTO(
        type_of_search=type_of_search,
        type_of_exploration="LCIENCC",
        expl_weight=expl_weight,
        is_concurrent=True,
        backhaul_network_available=True,
        use_expl=use_expl,
        use_custom_prob=use_custom_prob
    )

    cf = Control_function(area, base_stations, agents, users, dto)

    print("Initializing LoS matrix...")
    cf.initialize_LoS_matrix()
    print("Finished initializing LoS matrix")

    current_reward = cf.RCR_after_move()
    coverage_levels.append(current_reward)

    if use_expl:
        cf.update_probability_distribution_matrix(init=True)
        current_expl = cf.get_exploration_level()
        exploration_levels.append(current_expl)
        prob_matrix_history.append(cf.get_prob_matrix_snapshot())

    print(f"Start coverage level: {current_reward}")
    if use_expl:
        print(f"Start exploration level: {current_expl}")

    start = timer()
    t = 0

    # Pre-create a dict for quick agent id lookup
    agents_dict = {agent.id: agent for agent in agents}

    with ProcessPoolExecutor(max_workers=len(agents)) as executor: #creato fuori dal ciclo
                                                                   # cosi i processi vengono creati e distrutti una sola volta
        while t < NUM_OF_ITERATIONS:
            # Move users along their trajectories
            for user, trajectory in zip(users, user_trajectories):
                user.move_user_along_trajectory(trajectory, t)

            if dto.is_concurrent:
                # Prepare arguments for workers; pass only necessary cf info
                agent_args = [(agent, agents, t, {'cf': cf}) for agent in agents]
                results = list(executor.map(goal_worker, agent_args))
                # Update agents' goal points efficiently
                for agent_id, goal in results:
                    agents_dict[agent_id].goal_point = goal
            else:
                for agent in agents:
                    other_agents = [a for a in agents if a.id != agent.id]
                    agent.goal_point = cf.find_goal_point_for_agent(agent, other_agents, t)

            cf.move_agents()
            current_reward = cf.RCR_after_move()
            coverage_levels.append(current_reward)

            if use_expl:
                cf.update_probability_distribution_matrix()
                prob_matrix_history.append(cf.get_prob_matrix_snapshot())
                current_expl = cf.get_exploration_level()
                exploration_levels.append(current_expl)

            t += 1
            if type_of_search == "mixed" and t == NUM_OF_ITERATIONS // 2:
                type_of_search = "systematic mixed"

            log_msg = f"{type_of_search} iteration: {t} | coverage level: {current_reward}"
            if use_expl:
                log_msg += f" | exploration level: {current_expl}"
            print(log_msg)

            # Writing log less frequently (e.g., every 10 iterations)
            if t % 10 == 0 or t == NUM_OF_ITERATIONS:
                with open("logs/output_log.txt", 'a') as f:
                    f.write(log_msg + "\n")

    end = timer()
    time_elapsed = end - start

    print(f"Time elapsed: {time_elapsed:.2f}s")
    print(f"Final coverage level: {current_reward}")
    if use_expl:
        print(f"Final exploration level: {current_expl}")
    print(f"Simulation with desired coverage level: {DESIRED_COVERAGE_LEVEL}")

    # Map experiment id to folder path template
    experiment_paths = {
        1: f"Experiment results/experiment1/expl {use_expl}/BS {use_bs}/{num_of_iter}",
        2: f"Experiment results/experiment2/{type_of_search} search/{num_of_iter}",
        3: f"Experiment results/experiment3/custom prob {use_custom_prob}/{num_of_iter}",
    }

    exp_path = experiment_paths.get(experiment_id)
    if not exp_path:
        raise ValueError(f"Unknown experiment_id: {experiment_id}")

    print(f"Saving data in: {exp_path}")
    os.makedirs(exp_path, exist_ok=True)

    with open(os.path.join(exp_path, "time_elapsed.p"), "wb") as f:
        pickle.dump(time_elapsed, f)
    with open(os.path.join(exp_path, "coverages.p"), "wb") as f:
        pickle.dump(coverage_levels, f)

    if use_expl:
        with open(os.path.join(exp_path, "exploration_levels.p"), "wb") as f:
            pickle.dump(exploration_levels, f)

    print("Plotting results...")
    plot_area(area, users, base_stations, agents, type_of_search, num_of_iter,
              prob_matrix_history, expl_weight, use_expl, use_bs, use_custom_prob, path=exp_path)
    plot_coverage(coverage_levels, time_elapsed, type_of_search, expl_weight,
                  num_of_iter, use_expl, use_bs, use_custom_prob, path=exp_path)
    if use_expl:
        plot_exploration(exploration_levels, time_elapsed, type_of_search,
                         expl_weight, num_of_iter, use_bs, use_custom_prob, path=exp_path)
