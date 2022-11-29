import random
import csv
import threading

import schedule
import time
import os


class Generator:

    def __init__(self, shortname, type_):
        self.__isLoop = True
        self.__shortname = shortname
        self.__type_ = type_

    class Sensors:
        class SpeedSensor:
            def __init__(self):
                self._base_speed = 20  # base speed is 20 km/h

            def get_base_speed(self):
                return str(self._base_speed) + '_km_per_h'

            def set_base_speed(self, new_base_speed):
                self._base_speed = new_base_speed

            def get_speed(self):
                random_mix = random.randint(-10, 10)
                res = self._base_speed + random_mix
                return str(res) + '_km_per_h'

        class ProximitySensor:
            def __init__(self):
                self._base_proximity = 20  # base proximity is 20 meters

            def get_base_proximity(self):
                return str(self._base_proximity) + '_meters'

            def set_base_proximity(self, new_base_proximity):
                self._base_proximity = new_base_proximity

            def get_proximity(self):
                random_mix = random.randint(-10, 20000)
                res = self._base_proximity + random_mix
                return str(res) + '_meters'

        class PressureSensor:
            def __init__(self):
                self._base_pressure = 30  # base pressure is 30 psi

            def get_base_pressure(self):
                return str(self._base_pressure) + '_psi'

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
                return str(val) + '_psi'

        class LightSensor:
            def __init__(self):
                self._base_state = 'off'

            def get_base_state(self):
                return "light_is_" + self._base_state

            def set_base_state(self, new_state):
                self._base_state = new_state

            @staticmethod
            def get_state():
                state = ['on', 'off']
                return "light_is_" + random.choice(state)

        class WiperSensor:
            def __init__(self):
                self._base_state = 'off'

            def get_base_state(self):
                return "wiper_is_" + self._base_state

            def set_base_state(self, new_state):
                self._base_state = new_state

            @staticmethod
            def get_state():
                state = ['off', 'on_slow', 'on_medium', 'on_fast']
                return "wiper_is_" + random.choice(state)

        class PassengerSensor:
            def __init__(self):
                self._base_count = 0

            def get_base_count(self):
                return 'passenger_count_' + str(self._base_count)

            def set_base_count(self, new_count):
                self._base_count = new_count

            def get_count(self, vehicle_type):
                val = self._base_count
                if vehicle_type == 'car':
                    val = random.randint(1, 4)  # car
                elif vehicle_type == 'bike':
                    val = 1
                elif vehicle_type == 'truck':
                    val = random.randint(1, 2)  # bike, truck
                return 'passenger_count_' + str(val)

        class FuelSensor:
            def __init__(self):
                self._base_state = 'low'

            def get_base_state(self):
                return 'fuel_is_' + self._base_state

            def set_base_state(self, new_state):
                self._base_state = new_state

            @staticmethod
            def get_state():
                state = ['low', 'medium', 'full']
                return 'fuel_is_' + random.choice(state)

        class TemperatureSensor:
            def __init__(self):
                self._base_temp = 10

            def get_base_temp(self):
                return str(self._base_temp) + '_celsius_degree'

            def set_base_temp(self, new_temp):
                self._base_temp = new_temp

            def get_temp(self):
                random_mix = random.randint(-10, 30)
                res = self._base_temp + random_mix
                return str(res) + '_celsius_degree'

    def write_to_csv(self, device_name, device_type, sensor_type):
        if sensor_type == "speed":
            speed_sensor = self.Sensors.SpeedSensor()
            sensor_data = speed_sensor.get_speed()
        elif sensor_type == "proximity":
            proximity_sensor = self.Sensors.ProximitySensor()
            sensor_data = proximity_sensor.get_proximity()
        elif sensor_type == "pressure":
            pressure_sensor = self.Sensors.PressureSensor()
            sensor_data = pressure_sensor.get_pressure(device_type)
        elif sensor_type == "light":
            light_sensor = self.Sensors.LightSensor()
            sensor_data = light_sensor.get_state()
        elif sensor_type == "wiper":
            wiper_sensor = self.Sensors.WiperSensor()
            sensor_data = wiper_sensor.get_state()
        elif sensor_type == "passenger":
            passenger_sensor = self.Sensors.PassengerSensor()
            sensor_data = passenger_sensor.get_count(device_type)
        elif sensor_type == "fuel":
            fuel_sensor = self.Sensors.FuelSensor()
            sensor_data = fuel_sensor.get_state()
        elif sensor_type == "temperature":
            temp_sensor = self.Sensors.TemperatureSensor()
            sensor_data = temp_sensor.get_temp()
        else:
            sensor_data = "None"
        current_time = time.strftime("%Y%m%d%H%M")
        file_name = sensor_type + '.csv'

        file_path = './sensor_data/' + device_name + '/'
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        else:
            with open(file_path + file_name, "a") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([device_name, device_type, sensor_data, current_time])

    def execute_write_per_minute(self, sensor_type, device_name, device_type):
        schedule.every().minute.do(self.write_to_csv, device_name, device_type, sensor_type)

    def read_from_csv(self, device_name, sensor_type):
        try:
            sensor_types = ['speed', 'proximity', 'pressure', 'light', 'wiper', 'passenger', 'fuel', 'temperature']
            for i in sensor_types:
                if sensor_type == i:
                    file_path = './sensor_data/' + device_name + '/'
                    file_name = i + '.csv'
                    with open(file_path + file_name) as csvfile:
                        """
                        device_name, device_type, data, time = p1,car,19_km_per_h,202211290238
                        """
                        return csvfile.readlines()[-1]

        except Exception as e:
            return None

    # print(read_from_csv('speed'))

    def __task(self):
        self.execute_write_per_minute("speed", self.__shortname, self.__type_)
        self.execute_write_per_minute("temperature", self.__shortname, self.__type_)
        self.execute_write_per_minute("proximity", self.__shortname, self.__type_)
        self.execute_write_per_minute("light", self.__shortname, self.__type_)
        self.execute_write_per_minute("pressure", self.__shortname, self.__type_)
        self.execute_write_per_minute("wiper", self.__shortname, self.__type_)
        self.execute_write_per_minute("passenger", self.__shortname, self.__type_)
        self.execute_write_per_minute("fuel", self.__shortname, self.__type_)

        while True:
            if self.__isLoop:
                schedule.run_pending()
                time.sleep(1)

    def close(self):
        self.__isLoop = not self.__isLoop

    def run(self):
        try:
            t = threading.Thread(target=self.__task)
            t.setDaemon(True)
            t.start()

        except Exception as e:
            print(e)


if __name__ == '__main__':
    gen = Generator()
    gen.run()

    a = input()
    gen.close()

    while True:
        pass
