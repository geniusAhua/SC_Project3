import random


class Sensors:
    class SpeedSensor:
        def __init__(self):
            self._base_speed = 20  # base speed is 20 km/h

        def get_base_speed(self):
            return str(self._base_speed) + ' km/h'

        def set_base_speed(self, new_base_speed):
            self._base_speed = new_base_speed

        def get_speed(self):
            random_mix = random.randint(-10, 10)
            res = self._base_speed + random_mix
            return str(res) + ' km/h'

    class ProximitySensor:
        def __init__(self):
            self._base_proximity = 20  # base proximity is 20 meters

        def get_base_proximity(self):
            return str(self._base_proximity) + ' meters'

        def set_base_proximity(self, new_base_proximity):
            self._base_proximity = new_base_proximity

        def get_proximity(self):
            random_mix = random.randint(-10, 10)
            res = self._base_proximity + random_mix
            return str(res) + ' meters'

    class PressureSensor:
        def __init__(self):
            self._base_pressure = 30  # base pressure is 30 psi

        def get_base_pressure(self):
            return str(self._base_pressure) + ' psi'

        def set_base_pressure(self, new_base_pressure):
            self._base_pressure = new_base_pressure

        def get_pressure(self, vehicle_type):
            val = self._base_pressure
            if vehicle_type == 'car':
                val = random.randint(30, 33)  # car tyre pressure
            elif vehicle_type == 'bike':
                val = random.randint(80, 130)  # two-wheeler tyre pressure
            elif vehicle_type == 'truck':
                val = random.randint(116, 131)  # truck tyre pressure
            return str(val) + ' psi'

    class LightSensor:
        def __init__(self):
            self._base_state = 'off'

        def get_base_state(self):
            return self._base_state

        def set_base_state(self, new_state):
            self._base_state = new_state

        @staticmethod
        def get_state():
            state = ['on', 'off']
            return random.choice(state)

    class WiperSensor:
        def __init__(self):
            self._base_state = 'off'

        def get_base_state(self):
            return self._base_state

        def set_base_state(self, new_state):
            self._base_state = new_state

        @staticmethod
        def get_state():
            state = ['off', 'on-slow', 'on-medium', 'on-fast']
            return random.choice(state)

    class PassengerSensor:
        def __init__(self):
            self._base_count = 0

        def get_base_count(self):
            return self._base_count

        def set_base_count(self, new_count):
            self._base_count = new_count

        def get_count(self, vehicle_type):
            val = self._base_count
            if vehicle_type == 'car':
                val = random.randint(1, 4)  # car
            elif vehicle_type == 'bike' or vehicle_type == 'truck':
                val = random.randint(1, 2)  # bike, truck
            return str(val)

    class FuelSensor:
        def __init__(self):
            self._base_state = 'low'

        def get_base_state(self):
            return self._base_state

        def set_base_state(self, new_state):
            self._base_state = new_state

        @staticmethod
        def get_state():
            state = ['low', 'medium', 'full']
            return random.choice(state)

    class TemperatureSensor:
        def __init__(self):
            self._base_temp = 10

        def get_base_temp(self):
            return str(self._base_temp) + ' celsius degree'

        def set_base_temp(self, new_temp):
            self._base_temp = new_temp

        def get_temp(self):
            random_mix = random.randint(-10, 30)
            res = self._base_temp + random_mix
            return str(res) + ' celsius degree'
