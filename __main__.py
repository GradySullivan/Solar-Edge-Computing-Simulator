import time
import numpy as np
import csv
from edge_computing_system import *
from policies import *
from setup import *
from itertools import combinations


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


if __name__ == '__main__':
    start_time = time.time()  # start timer

    num_edges, num_servers, server_cores, server_memory, power_per_server, edge_pv_efficiency, edge_pv_area, \
    trace_info, irradiance_info = config_setup()  # variables configured by config file

    edge_computing_systems = {}  # dictionary: edge_site:servers

    edge_computing_systems = generate_nodes(num_edges, num_servers, edge_pv_efficiency, edge_pv_area, server_cores,
                                            server_memory)  # generate dictionary with node:server(s) pairs

    location_distances = get_distances(edge_computing_systems)

    applications = generate_applications(trace_info)  # generate list of application instances

    irradiance_list = generate_irradiance_list(irradiance_info)  # generate list of irradiances

    check_min_req(applications, edge_computing_systems, server_cores, server_memory)  # prevents infinite loops

    # ------------------ simulation ----------------

    processing_time = -1  # counter to tally simulation time (-1 indicates not started yet)

    while len(applications) != 0 or all_servers_empty is False:

        processing_time += 1
        print(f'Time = {processing_time}')

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
                if power == 0:  # turn off all servers if no power
                    #print('shutting down all servers')
                    for server in edge.servers:
                        server.on = False
                    server_power_updated = True
                elif power / servers_on < power_per_server:  # determine how to shut down sites
                    #print('power', power)
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
                            for server in edge.servers:
                                server.on = False
                            break
                    server_power_updated = True
                else:
                    server_power_updated = True
        complete_applications(edge_computing_systems)
        start_applications(edge_computing_systems, applications) # start applications
        all_servers_empty = get_applications_running(edge_computing_systems)  # check if applications are running

    simplify_time(processing_time)  # simulation time
    print(f'Execution Time: {time.time() - start_time}')  # end timer
