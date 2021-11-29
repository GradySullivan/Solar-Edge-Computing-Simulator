import itertools
import time
import random
import csv
from geopy.distance import geodesic as gd
from datetime import datetime

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


def get_empty_queue(edge_computing_systems: list):
    """
    :param edge_computing_systems: list of nodes
    :return: boolean
    """
    for node in edge_computing_systems:
        if node.queue:
            return False
    return True


def split(a: list, n: int):
    """
    :param a: list to split
    :param n: how many parts to split list into
    :return: split list
    """
    k, m = divmod(len(a), n)
    return [a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n)]


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
    random.seed(1)
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
    policy = config_info['Policy'].strip()
    global_applications = True if config_info['Global Applications'].strip() == "True" else False
    trace_info = config_info['Traces'].strip()
    irradiance_info = config_info['Irradiance List'].strip()
    diagnostics = True if (config_info['Diagnostics'].strip()) == "True" else False

    coords = config_info['Coords']

    edge_computing_systems = generate_nodes(num_edges, num_servers, edge_pv_efficiency, edge_pv_area, server_cores,
                                            server_memory, battery, coords, node_placement)

    shortest_distances, location_distances = get_shortest_distances(edge_computing_systems)

    applications = generate_applications(trace_info)  # generate list of application instances
    total_applications = len(applications)
    split_applications = split(applications, len(edge_computing_systems))

    if global_applications is False:
        for index, node in enumerate(edge_computing_systems):
            node.queue = split_applications[index]
    else:
        edge_computing_systems[0].queue = applications

    irradiance_list = generate_irradiance_list(irradiance_info)  # generate list of irradiance values

    check_min_req(applications, server_cores, server_memory)  # prevents infinite loops

    # lists to store results
    simulated_time_results = []
    queue_results = []
    cumulative_paused_applications_results = []
    current_paused_applications_results = []
    cumulative_migrations_results = []
    current_migrations_results = []
    cumulative_completion_results = []
    completion_rate_results = []

    # ---------------- simulation ----------------

    processing_time = -1  # counter to tally simulation time (-1 indicates not started yet)
    all_servers_empty = False
    all_empty_queues = False
    partially_completed_applications = []

    while all_empty_queues is False or len(partially_completed_applications) != 0 or all_servers_empty is False:
        processing_time += 1
        if processing_time > 100000000:
            print('ERROR: exceeding 100,000,000 iterations')
            quit()

        simulated_time_results.append(processing_time)

        total_queue_length = 0
        for node in edge_computing_systems:
            total_queue_length += len(node.queue)
        queue_results.append(total_queue_length)

        if diagnostics:
            print(f'Time = {processing_time}')
            print(f'Queue Length: {total_queue_length}')
            print(f'Partial: {len(partially_completed_applications)}')

        current_completed = complete_applications(edge_computing_systems, diagnostics)

        if len(cumulative_completion_results) == 0:
            cumulative_completion_results.append(current_completed)
        else:
            cumulative_completion_results.append(cumulative_completion_results[-1] + current_completed)
        completion_rate_results.append(cumulative_completion_results[-1] / total_applications)

        current_paused_applications = shutdown_servers(edge_computing_systems, power_per_server, irradiance_list,
                                                       processing_time, partially_completed_applications, diagnostics)

        current_paused_applications_results.append(current_paused_applications)
        if len(cumulative_paused_applications_results) == 0:
            cumulative_paused_applications_results.append(current_paused_applications)
        else:
            cumulative_paused_applications_results.append(cumulative_paused_applications_results[-1]
                                                          + current_paused_applications)

        current_migrations = resume_applications(policy, partially_completed_applications, shortest_distances,
                                                 cost_multiplier, edge_computing_systems, irradiance_list,
                                                 processing_time, power_per_server, diagnostics)

        current_migrations_results.append(current_migrations)
        if len(cumulative_migrations_results) == 0:
            cumulative_migrations_results.append(current_migrations)
        else:
            cumulative_migrations_results.append(cumulative_migrations_results[-1] + current_migrations)

        start_applications(edge_computing_systems, global_applications, diagnostics)

        if battery > 0:
            update_batteries(edge_computing_systems, power_per_server, irradiance_list, processing_time)

        all_empty_queues = get_empty_queue(edge_computing_systems)
        all_servers_empty = get_applications_running(edge_computing_systems)  # check if applications are running

    simplify_time(processing_time)  # simulation time
    print(f'Execution Time: {time.time() - start_time}')  # end timer

    # write results to text file
    now = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
    with open(f'Outputs/{policy}_output_{now}.txt', 'w') as file:
        with open('config.txt', 'r') as config:
            reader = config.readlines()
        for line in reader:
            file.write(line)
        file.write('\n----------------\n')
        file.write('Application Completion Locations\n')
        for node in edge_computing_systems:
            file.write(f'Node {node.index}: {node.applications_completed}\n')
        file.write('----------------\n')
        file.write('Simulated Time, Queue Length, Currently Paused, Cumulative Paused Applications, Current '
                   'Migrations, Cumulative Migrations, Cumulative Completions, Completion %\n')
        for index, value in enumerate(simulated_time_results):
            file.write(f'{str(value)}, ')
            file.write(f'{str(queue_results[index])}, ')
            file.write(f'{str(current_paused_applications_results[index])}, ')
            file.write(f'{str(cumulative_paused_applications_results[index])}, ')
            file.write(f'{str(current_migrations_results[index])}, ')
            file.write(f'{str(cumulative_migrations_results[index])}, ')
            file.write(f'{str(cumulative_completion_results[index])}, ')
            file.write(f'{str(completion_rate_results[index])}, ')
            file.write('\n')


if __name__ == '__main__':
    main()

    '''with cProfile.Profile() as pr:
        main()
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()'''