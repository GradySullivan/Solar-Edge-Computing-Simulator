import time
import numpy as np
from setup import *


class EdgeSystem:
    def __init__(self, pv_efficiency, pv_area):
        self.pv_efficiency = pv_efficiency  # between 0 and 1
        self.pv_area = pv_area  # in m^2
        self.servers = []
        self.lat = None
        self.long = None

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

        def start_application(self):
            print('processing', application)
            self.update_resources('reduce', application)
            self.applications_running[application] = application.time_left  # application in "running" dict

        def stop_application(self):
            print('completed', application)
            self.update_resources('restore', application)
            del self.applications_running[application]  # delete from applications list if completed


class Application:
    def __init__(self, runtime, cores, memory):
        self.runtime = runtime
        self.cores = cores
        self.memory = memory
        self.time_left = runtime


def get_applications_running(edge_dictionary):
    for server_list in edge_dictionary.values():
        for server in server_list:
            if server.applications_running != {}:
                return False
    return True


def simplify_time(sec):
    day, hr, minute = 0, 0, 0
    if sec >= 60:
        minute = sec // 60
        sec = sec % 60
        if minute >= 60:
            hr = minute // 60
            minute = minute % 60
            if hr >= 24:
                day = hr // 24
                hr = hr % 24
    if day > 0:
        print(f'[Simulated Time] {day} day(s), {hr} hour(s), {minute} minute(s), {sec} second(s)')
    elif hr > 0:
        print(f'[Simulated Time] {hr} hour(s), {minute} minute(s), {sec} second(s)')
    elif minute > 0:
        print(f'[Simulated Time] {minute} minute(s), {sec} second(s)')
    else:
        print(f'[Simulated Time] {sec} second(s)')


def generate_nodes(num_edges, num_servers):
    edge_computing_systems = {}  # dictionary: edge_site:servers
    edges = np.array([])
    servers = np.array([])

    # create edge sites
    for edge in range(num_edges):
        edge_site = EdgeSystem(edge_pv_efficiency, edge_pv_area)
        for server in range(num_servers):
            servers = np.append(servers, edge_site.get_server_object(server_cores, server_memory))
        edge_site.servers = servers
        edge_computing_systems[edge_site] = servers
    return edge_computing_systems


def generate_applications(file):
    # create applications
    applications = []  # initialize list of class instances
    with open(file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)  # skip header
        for row in csv_reader:
            runtime = int(row[2])
            cores = int(row[3])
            try:
                memory = int(row[5])
            except:
                continue
            applications.append(Application(runtime, cores, memory))  # instance for each application
    return applications


if __name__ == '__main__':
    start_time = time.time()  # start timer

    num_edges, num_servers, server_cores, server_memory, power_per_server, edge_pv_efficiency, edge_pv_area, \
        trace_info, irradiance_info = config_setup()  # variables configured by config file

    edge_computing_systems = generate_nodes(num_edges, num_servers)  # generate dictionary with node:server(s) pairs
    applications = generate_applications(trace_info)  # generate list of application instances
    irradiance_list = generate_irradiance_list(irradiance_info)  # generate list of irradiances
    check_min_req(applications, edge_computing_systems, server_cores, server_memory)  # checks minimum requirements to prevent infinite loops

    # ------------------ simulation ----------------

    processing_time = -1  # counter to tally simulation time (-1 indicates not started yet)

    while len(applications) != 0 or all_servers_empty is False:

        processing_time += 1
        print(f'Time = {processing_time}')
        processing = []

        # determine which servers are on
        for edge in edge_computing_systems.keys():  # start by turning all servers back on
            for server in edge.servers:
                server.on = True
        server_power_updated = False

        # turn off servers w/o enough power (priority to keep servers on that are closest to completing a task)
        while server_power_updated is False:
            for edge in edge_computing_systems.keys():
                servers_on = num_servers
                power = edge.get_power_generated(irradiance_list[processing_time])  # update power available to edges
                '''print('------------')
                print('power', power)
                print('servers on', servers_on)
                print('p/s', power / servers_on)
                print('pps', power_per_server)'''
                if power == 0:  # turn off all servers if no power
                    print('shutting down all servers')
                    for server in edge.servers:
                        server.on = False
                    server_power_updated = True
                elif power / servers_on < power_per_server:  # determine how to shut down sites
                    application_progression = {}
                    while power / servers_on < power_per_server and servers_on > 0:
                        for server in edge.servers:
                            if server.applications_running == {}:
                                server.on = False
                                servers_on -= 1
                                break
                            application_progression[server] = max(server.applications_running).time_left
                        if application_progression != {}:
                            min_server = max(application_progression, key=application_progression.get)
                            min_server.on = False
                            del application_progression[min_server]
                            servers_on -= 1
                        if servers_on == 0:
                            print('shutting down all servers')
                            for server in edge.servers:
                                server.on = False
                            break
                    server_power_updated = True
                else:
                    server_power_updated = True

        # completing applications
        for edge in edge_computing_systems.keys():  # for each edge computing site...
            for server in edge.servers:  # for each server in a particular edge site
                if server.on is True:
                    for application in list(server.applications_running.keys()):  # for each application running...
                        if application not in processing:  # if the application wasn't added in this time iteration...
                            application.time_left -= 1
                            # print(application, 'Time Left', application.time_left)
                            if application.time_left <= 0:
                                server.stop_application()
                            processing.append(application)  # to prevent application decrementing multiple times

        # start applications
        for edge in edge_computing_systems.keys():  # for each edge computing site...
            for server in edge.servers:  # for each server in a particular edge site
                if server.on is True:
                    for application in list(applications):  # for each application that still needs to run
                        if (application.memory <= server.memory) and (application.cores <= server.cores):
                            server.start_application()
                            applications.remove(application)  # remove from to-do list

        all_servers_empty = get_applications_running(edge_computing_systems)  # check if applications are running

    simplify_time(processing_time)  # simulation time
    print(f'Execution Time: {time.time() - start_time}')  # end timer
