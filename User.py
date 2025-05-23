import pickle
import random

import numpy as np
import math
from Constants import *


class User:
    id = 0  # incremental id attribute, static attribute

    def __init__(self, area, desired_coverage_level, deserialize=False):
        self.__x = None
        self.__y = None
        self.id = User.id
        User.id += 1

        # if deserialize is True, the position of the user is loaded from serialized file (using pickle module)
        # else assign random position, after that serialize the object and save it in the specified file
        if deserialize:
            self.__x, self.__y = pickle.load(open("User position/user" + str(self.id) + ".p", "rb"))
        else:
            self.__x, self.__y = random.uniform(0, area.length), random.uniform(0, area.width)
            pickle.dump((self.__x, self.__y), open("User position/user" + str(self.id) + ".p", "wb"))

        # defining other attributes
        self.area = area
        self.desired_coverage_level = desired_coverage_level
        self.is_covered = None
        self.coverage_history = []

        self.theta = random.uniform(0, 2 * math.pi)  # Orientation angle in radians

        self.trajectory_history = [(self.__x, self.__y)]

    def set_is_covered(self, is_covered):
        self.is_covered = is_covered
        self.coverage_history.append(is_covered)  # also updates user's coverage history

    def get_position(self):
        return self.__x, self.__y

    def get_3D_position(self):
        return self.get_position() + (0,)

    def set_position(self, x, y):
        self.__x = x
        self.__y = y

    #Removed move fucntion

    def simulate_trajectory(self, steps, area_width, area_length):
        """
        DEBUG VERSION: Simulates a trajectory where the user moves strictly upward (along +Y axis)
        without modifying the actual user position.

        :param steps: Number of time steps to simulate
        :param area_width: Width of the area (used to bound the simulated positions)
        :param area_length: Length of the area (used to bound the simulated positions)
        :return: List of (x, y) positions representing the simulated trajectory
        """
        x, y = self.__x, self.__y

        trajectory = []

        for _ in range(steps):
            v = max(0.0, random.gauss(USER_VELOCITY_MEAN, USER_VELOCITY_STD))

            # Move strictly upward (dy = v, dx = 0)
            dx = 0
            dy = v

            # Apply bounds
            y = min(max(y + dy, 0), area_length)

            trajectory.append((x, y))

        return trajectory

    def simulate_trajectory_ct(self, steps, area_width, area_length):
        """
        Simulates a trajectory using a refined coordinated turn model.
        """
        x, y = self.__x, self.__y
        theta = self.theta

        # Initial velocity and angular velocity
        v = max(0.0, random.gauss(USER_VELOCITY_MEAN, USER_VELOCITY_STD))
        omega = random.gauss(0.0, USER_ANGULAR_VELOCITY_STD)

        trajectory = []

        alpha = 0.85  # Smoothing factor
        beta = 0.2  # Heading persistence
        gamma = 0.4  # Speed-turn coupling

        for _ in range(steps):
            # New "intended" velocities
            target_v = max(0.0, random.gauss(USER_VELOCITY_MEAN, USER_VELOCITY_STD))
            target_omega = random.gauss(0.0, USER_ANGULAR_VELOCITY_STD)

            # Smooth update
            v = alpha * v + (1 - alpha) * target_v

            # Turn rate coupling: slower speed = more turning freedom
            max_turn = min(1.0, gamma / max(v, 0.1))
            target_omega = max(-max_turn, min(max_turn, target_omega))
            omega = alpha * omega + (1 - alpha) * target_omega

            # Persistent heading drift (makes arcs longer-lasting)
            theta = (theta + omega + beta * omega) % (2 * math.pi)

            # Motion
            dx = v * math.cos(theta)
            dy = v * math.sin(theta)

            # Keep in bounds
            x = min(max(x + dx, 0), area_width)
            y = min(max(y + dy, 0), area_length)

            trajectory.append((x, y))

        return trajectory

    def move_user_along_trajectory(self,trajectory,i):
            """
            Updates the user's position based on the i-th position in the trajectory.
            Also updates the trajectory history accordingly.

            :param trajectory: List of (x, y) positions representing the trajectory
            :param i: Index of the desired position in the trajectory
            """
            if i < 0 or i >= len(trajectory):
                raise IndexError("Index out of bounds of trajectory list.")

            x, y = trajectory[i]
            self.set_position(x, y)
            self.trajectory_history.append((x, y))

