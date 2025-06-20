import pickle
import random

from Constants import *

class Sensor:
    id = 0  # incremental id of all sensors, static attribute

    def __init__(self, area, communication_radius, transmitting_power, altitude):
        self.id = Sensor.id
        Sensor.id += 1

        # random placement, except for the altitude to prevent collision between agents
        self._x, self._y = random.uniform(0, area.width), random.uniform(0, area.length)

        self._previous_x, self._previous_y = self._x,self._y # at first lets put previous the same as the current

        # set spawn point for agents at base station
        # spawn_point_list = [(1 / 4 * area.width, 1 / 4 * area.length), (1 / 4 * area.width, 3 / 4 * area.length), (3 / 4 * area.width, 1 / 4 * area.length), (3 / 4 * area.width, 3 / 4 * area.length)]
        # self._x, self._y = random.choice(spawn_point_list)

        self._z = altitude

        # assignment of other parameters
        self.area = area
        self.transmitting_power = transmitting_power
        self.communication_radius = communication_radius

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def get_previous_x(self):
        return self._previous_x

    def get_previous_y(self):
        return self._previous_y

    def get_z(self):
        return self._z

    def get_2D_position(self):
        return self._x, self._y

    def get_2D_previous_position(self):
        return self._previous_x,self._previous_y

    def get_3D_position(self):
        return self._x, self._y, self._z


class Agent(Sensor):

    def __init__(self, area, communication_radius, transmitting_power, altitude, deserialize=False):
        super().__init__(area, communication_radius, transmitting_power, altitude)

        # if deserialize is True, the position of the sensor is loaded from serialized file (using pickle module)
        # else serialize and save the position of the sensor (which is random assigned by super constructor)
        if deserialize:
            self._x, self._y = pickle.load(open("Sensor position/sensor" + str(self.id) + ".p", "rb"))
        else:
            pickle.dump((self._x, self._y), open("Sensor position/sensor" + str(self.id) + ".p", "wb"))

        # setting a starting point for goal-searching
        self.goal_point = (self._x, self._y)
        self.trajectory = [(self._x, self._y)]

    def set_2D_position(self, x, y):
        self._x = x
        self._y = y

    def set_x(self, x):
        self._x = x

    def set_y(self, y):
        self._y = y

    def set_2D_previous_position(self, x, y):
        self._previous_x = x
        self._previous_y = y

    def set_previous_x(self, x):
        self._previous_x = x

    def set_previous_y(self, y):
        self._previous_y= y


class Base_station(Sensor):
    def __init__(self, area, communication_radius, x, y, scenario, interference_by_bs=False):

        # Define Tx power and altitude per scenario
        if scenario == "Suburban":
            #altitude = 30  # meters
            #transmitting_power = 30  # watts (between 20-40 W)
            altitude = 30  # meters
            transmitting_power = 30  # watts (between 20-40 W)
        elif scenario == "Urban":
            altitude = 75  # meters (between 50-100 m)
            transmitting_power = 15  # watts (between 10-20 W)
        elif scenario == "Dense Urban":
            altitude = 125  # meters (between 100-150 m)
            transmitting_power = 7.5  # watts (between 5-10 W)
        elif scenario == "Highrise Urban":
            altitude = 250  # meters (between 150-300 m)
            transmitting_power = 3  # watts (between 1-5 W)
        else:
            # Default values if unknown scenario
            altitude = 30
            transmitting_power = 20

        super().__init__(area, communication_radius, transmitting_power, altitude)

        self.altitude = altitude

        # Setting if the base station can interfere with agents
        self.interference_by_bs = interference_by_bs

        self._x = x
        self._y = y
