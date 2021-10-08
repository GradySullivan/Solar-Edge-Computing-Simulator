class EdgeSystem:
    def __init__(self, pv_efficiency, pv_area, lat, long):
        self.pv_efficiency = pv_efficiency  # between 0 and 1
        self.pv_area = pv_area  # in m^2
        self.servers = []
        self.lat = lat
        self.long = long

    def get_server_object(self, cores, memory):
        return self.Server(cores, memory)

    def get_power_generated(self, irradiance):
        # P_n = eta * G_T * A_n
        return self.pv_efficiency * irradiance * self.pv_area

    class Server:
        def __init__(self, cores, memory):
            self.cores = cores  # per server
            self.memory = memory  # per server, in MB
            self.on = False
            self.applications_running = {}

        def update_resources(self, decision, app):
            if decision == 'restore':
                self.cores += app.cores  # cores available increases
                self.memory += app.memory  # memory available increases
            if decision == 'reduce':
                self.cores -= app.cores  # cores available increases
                self.memory -= app.memory  # memory available increases

        def start_application(self, application):
            #print('processing', application)
            self.update_resources('reduce', application)
            self.applications_running[application] = application.time_left  # application in "running" dict

        def stop_application(self, application):
            print('completed', application)
            self.update_resources('restore', application)
            del self.applications_running[application]  # delete from applications list if completed


class Application:
    def __init__(self, runtime, cores, memory):
        self.runtime = runtime
        self.cores = cores
        self.memory = memory
        self.time_left = runtime