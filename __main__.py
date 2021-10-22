import itertools
import time
import random
import csv
import numpy as np

from edge_computing_system import *
from policies import *
from setup import *

import cProfile
import pstats


def get_applications_running(edge_dictionary):
    for node in edge_dictionary.values():
        for server in node:
            if server.applications_running:
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


def main():
    #random.seed(1)
    start_time = time.time()  # start timer

    # can be changed in config.txt
    config_info, coords = config_setup()
    num_edges = int(config_info['Nodes'])
    num_servers = int(config_info['Servers per Node'])
    server_cores = int(config_info['Cores per Server'])
    server_memory = int(config_info['Memory per Server'])
    power_per_server = float(config_info['Power per Server Needed'])
    edge_pv_efficiency = float(config_info['PV Efficiency'])
    edge_pv_area = float(config_info['PV Area'])
    node_placement = config_info['Node Placement'].strip()
    global_applications = True if config_info['Global Applications'].strip() == "True" else False
    trace_info = config_info['Traces'].strip()
    irradiance_info = config_info['Irradiance List'].strip()

    edge_computing_systems = generate_nodes(num_edges, num_servers, edge_pv_efficiency, edge_pv_area, server_cores,
                                            server_memory, coords, node_placement)  # generate dictionary with node:server(s) pairs

    location_distances = get_distances(edge_computing_systems, num_edges)
    shortest_distances = get_shortest_distances(edge_computing_systems, location_distances, num_edges)

    applications = generate_applications(trace_info)  # generate list of application instances

    irradiance_list = generate_irradiance_list(irradiance_info)  # generate list of irradiances

    check_min_req(applications, edge_computing_systems, server_cores, server_memory)  # prevents infinite loops

    # ------------------ simulation ----------------

    processing_time = -1  # counter to tally simulation time (-1 indicates not started yet)
    all_servers_empty = False
    partially_completed_applications = []

    while len(applications) != 0 or len(partially_completed_applications) != 0 or all_servers_empty is False:

        processing_time += 1
        print(f'Time = {processing_time}')

        complete_applications(edge_computing_systems)

        shutdown_servers(edge_computing_systems, num_servers, power_per_server, irradiance_list, processing_time,
                         partially_completed_applications, applications)

        partially_completed_applications = resume_applications(edge_computing_systems, partially_completed_applications, shortest_distances)

        start_applications(edge_computing_systems, applications, global_applications)  # start applications

        all_servers_empty = get_applications_running(edge_computing_systems)  # check if applications are running

    simplify_time(processing_time)  # simulation time
    print(f'Execution Time: {time.time() - start_time}')  # end timer


if __name__ == '__main__':
    main()

    '''with cProfile.Profile() as pr:
        main()

    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()'''