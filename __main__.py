import time
import random
from itertools import combinations
from geopy.distance import geodesic as gd
from setup import *
from policies import *


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

    edge_computing_systems = generate_nodes(num_edges, num_servers, edge_pv_efficiency, edge_pv_area, server_cores,
                                            server_memory)  # generate dictionary with node:server(s) pairs

    location_distances = {}  # dictionary lookup table; (loc1, loc2): distance
    if len(edge_computing_systems) > 1:  # only does if more than one node
        combos = combinations(edge_computing_systems, 2)  # every combination of two nodes
        for pair in combos:
            loc1 = (pair[0].lat, pair[0].long)  # coordinates for location 1
            loc2 = (pair[1].lat, pair[1].long)  # coordinates for location 2
            location_distances[pair] = gd(loc1, loc2)  # calculate distance between locations in km, add to dictionary

    applications = generate_applications(trace_info)  # generate list of application instances

    irradiance_list = generate_irradiance_list(irradiance_info)  # generate list of irradiances

    check_min_req(applications, edge_computing_systems, server_cores, server_memory)  # prevents infinite loops

    # ------------------ simulation ----------------

    processing_time = -1  # counter to tally simulation time (-1 indicates not started yet)
    partially_completed_applications = []  # apps that started running, but were shut down due to power constraints

    while len(applications) != 0 or len(partially_completed_applications) or all_servers_empty is False:

        processing_time += 1
        print(f'Time = {processing_time}')

        applications = shutdown_servers(edge_computing_systems, partially_completed_applications, num_servers, power_per_server,
                         irradiance_list, processing_time, applications)
        complete_applications(edge_computing_systems)  # completing applications

        start_applications(edge_computing_systems, applications)  # start new applications if resources available
        all_servers_empty = get_applications_running(edge_computing_systems)  # check if applications are running

    simplify_time(processing_time)  # simulation time
    print(f'Execution Time: {time.time() - start_time}')  # end timer
