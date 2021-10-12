import time
import numpy as np
import csv
from edge_computing_system import *
from policies import *
from setup import *
from itertools import combinations
import random


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
    #random.seed(1)
    start_time = time.time()  # start timer

    num_edges, num_servers, server_cores, server_memory, power_per_server, edge_pv_efficiency, edge_pv_area, \
    trace_info, irradiance_info = config_setup()  # variables configured by config file

    edge_computing_systems = {}  # dictionary: edge_site:servers

    edge_computing_systems = generate_nodes(num_edges, num_servers, edge_pv_efficiency, edge_pv_area, server_cores,
                                            server_memory)  # generate dictionary with node:server(s) pairs

    location_distances = get_distances(edge_computing_systems, num_edges)
    shortest_distances = get_shortest_distances(edge_computing_systems, location_distances, num_edges)

    applications = generate_applications(trace_info)  # generate list of application instances

    irradiance_list = generate_irradiance_list(irradiance_info)  # generate list of irradiances

    check_min_req(applications, edge_computing_systems, server_cores, server_memory)  # prevents infinite loops

    # ------------------ simulation ----------------

    processing_time = -1  # counter to tally simulation time (-1 indicates not started yet)
    partially_completed_applications = []
    while len(applications) != 0 or len(partially_completed_applications) != 0 or all_servers_empty is False:
        processing_time += 1
        print(f'Time = {processing_time}')

        applications, partially_completed_applications = shutdown_servers(edge_computing_systems, num_servers, power_per_server, irradiance_list,
                                        processing_time, partially_completed_applications, applications)

        complete_applications(edge_computing_systems)
        partially_completed_applications = decrement_transfer_time(partially_completed_applications)

        applications, partially_completed_applications = shutdown_servers(edge_computing_systems, num_servers, power_per_server, irradiance_list,
                                        processing_time, partially_completed_applications, applications)
        start_applications(edge_computing_systems, partially_completed_applications, shortest_distances)
        start_applications(edge_computing_systems, applications, None)  # start applications

        all_servers_empty = get_applications_running(edge_computing_systems)  # check if applications are running
        #print(len(applications), len(partially_completed_applications))
        '''for edge in edge_computing_systems.keys():
            for server in edge.servers:
                print(server, server.on, server.memory, server.cores, server.applications_running)'''
    simplify_time(processing_time)  # simulation time
    print(f'Execution Time: {time.time() - start_time}')  # end timer
