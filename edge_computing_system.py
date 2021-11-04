from __main__ import *

class EdgeSystem:
    def __init__(self, pv_efficiency: float, pv_area: float, lat: float, long: float, battery: float, index: int):
        self.pv_efficiency = pv_efficiency  # between 0 and 1
        self.pv_area = pv_area  # in m^2
        self.servers = []
        self.lat = lat
        self.long = long
        self.current_battery = 0
        self.max_battery = battery
        self.index = index

    def get_server_object(self, cores: int, memory: int, edge: object):
        return self.Server(cores, memory, edge)

    def get_power_generated(self, irradiance: float):
        # P_n = eta * G_T * A_n
        return self.pv_efficiency * irradiance * self.pv_area

    class Server:
        def __init__(self, cores: int, memory: float, edge: object):
            self.cores = cores  # per server
            self.memory = memory  # per server, in MB
            self.on = False
            self.applications_running = []
            self.parent = edge

        def update_resources(self, decision: str, app: object):
            if decision == 'restore':
                self.cores += app.cores  # cores available increases
                self.memory += app.memory  # memory available increases
            if decision == 'reduce':
                self.cores -= app.cores  # cores available increases
                self.memory -= app.memory  # memory available increases

        def start_application(self, application: object):
            self.update_resources('reduce', application)
            self.applications_running.append(application)
            application.parent = self

        def stop_application(self, application: object):
            if application.time_left == 0:
                print('completed', application, 'at', application.parent)
            self.update_resources('restore', application)
            self.applications_running.remove(application)  # delete from applications list if completed


class Application:
    def __init__(self, runtime: int, cores: int, memory: int):
        self.runtime = runtime
        self.cores = cores
        self.memory = memory
        self.time_left = runtime
        self.parent = None
        self.delay = None