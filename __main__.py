import itertools
import time
import random
import csv
from geopy.distance import geodesic as gd

from edge_computing_system import *
from policies import *
from setup import *

import cProfile
import pstats


def get_applications_running(edge_computing_systems: list):
    """

    :param edge_computing_systems: list of nodes
    :return: boolean
    """
    """Determines if any servers among any of the nodes are currently running applications"""
    for node in edge_computing_systems:
        for server in list(node.servers):
            if server.applications_running:
                return False
    return True


def simplify_time(sec: int):
    """

    :param sec: simulated seconds for how long it took for applications to complete
    :return: None
    """
    """Converts simulated seconds and converts into minutes, hours, and days for diagnostic printing"""
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
    config_info = config_setup()
    num_edges = int(config_info['Nodes'])
    num_servers = int(config_info['Servers per Node'])
    server_cores = int(config_info['Cores per Server'])
    server_memory = int(config_info['Memory per Server'])
    battery = float(config_info['Battery Size'])  # measured in Watt-hours
    power_per_server = float(config_info['Power per Server Needed'])
    edge_pv_efficiency = float(config_info['PV Efficiency'])
    edge_pv_area = float(config_info['PV Area'])
    cost_multiplier = float(config_info['Cost Multiplier'])
    node_placement = config_info['Node Placement'].strip()
    global_applications = True if config_info['Global Applications'].strip() == "True" else False
    trace_info = config_info['Traces'].strip()
    irradiance_info = config_info['Irradiance List'].strip()
    coords = config_info['Coords']

    edge_computing_systems = generate_nodes(num_edges, num_servers, edge_pv_efficiency, edge_pv_area, server_cores,
                                            server_memory, battery, coords, node_placement)

    shortest_distances = get_shortest_distances(edge_computing_systems)

    applications = generate_applications(trace_info)  # generate list of application instances
    total_applications = len(applications)
    print(f'TOTAL APPLICATIONS: {total_applications}')

    irradiance_list = generate_irradiance_list(irradiance_info)  # generate list of irradiance values

    check_min_req(applications, server_cores, server_memory)  # prevents infinite loops

    # ---------------- simulation ----------------

    processing_time = -1  # counter to tally simulation time (-1 indicates not started yet)
    all_servers_empty = False
    partially_completed_applications = []

    while len(applications) != 0 or len(partially_completed_applications) != 0 or all_servers_empty is False:

        processing_time += 1
        print(f'Time = {processing_time}')
        #print(f'Percent of Applications Remaining: {len(applications) / total_applications}')

        complete_applications(edge_computing_systems)

        shutdown_servers(edge_computing_systems, power_per_server, irradiance_list, processing_time,
                         partially_completed_applications)

        resume_applications(partially_completed_applications, shortest_distances, cost_multiplier)

        if applications:
            start_applications(edge_computing_systems, applications, global_applications)  # start applications

        if battery > 0:
            update_batteries(edge_computing_systems, power_per_server, irradiance_list, processing_time)

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