import itertools
import time
import random
import csv
from geopy.distance import geodesic as gd
from datetime import datetime

from edge_computing_system import *
from policies import *
from setup import *


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
    start_time = time.time()  # start timer
    get_node_info()

    # can be changed in config.txt
    config_info = config_setup()
    num_edges, coords = get_node_info()
    num_servers = int(config_info['Servers per Node'])
    server_cores = int(config_info['Cores per Server'])
    server_memory = int(config_info['Memory per Server'])
    battery = float(config_info['Battery Size'])  # measured in Watts
    power_per_server = float(config_info['Power per Server Needed'])
    edge_pv_efficiency = float(config_info['PV Efficiency'])
    edge_pv_area = float(config_info['PV Area'])
    delay_function = config_info['Delay Function']
    node_placement = config_info['Node Placement'].strip()
    policy = config_info['Policy'].strip()
    global_applications = True if config_info['Global Applications'].strip() == "True" else False
    degradable_applications = True if config_info['Degradable Applications'].strip() == "True" else False
    degradable_multiplier = float(config_info['Degradable Multiplier'])
    trace_info = config_info['Traces'].strip()
    irradiance_info = config_info['Irradiance List'].strip()
    diagnostics = True if (config_info['Diagnostics'].strip()) == "True" else False

    edge_computing_systems = generate_nodes(num_edges, num_servers, edge_pv_efficiency, edge_pv_area, server_cores,
                                            server_memory, battery, coords, node_placement)

    shortest_distances, location_distances = get_shortest_distances(edge_computing_systems)

    applications = generate_applications(trace_info)  # generate list of application instances
    completed_applications = []
    total_applications = len(applications)
    location_distances = get_distances(edge_computing_systems)
    irradiance_list = generate_irradiance_list(irradiance_info)  # generate list of irradiance values
    check_min_req(applications, server_cores, server_memory, degradable_applications)  # prevents infinite loops

    # results
    simulated_time_results = []
    queue_results = []
    cumulative_paused_applications_results = []
    current_paused_applications_results = []
    cumulative_migrations_results = []
    current_migrations_results = []
    cumulative_completion_results = []
    completion_rate_results = []
    total_overhead = 0

    sec_per_day = 86400
    # ---------------- simulation ----------------

    processing_time = -1 + sec_per_day  # counter to tally simulation time (-1 indicates not started yet)
    all_servers_empty = False
    partially_completed_applications = []
    max_iterations = 100000000
    while len(applications) != 0 or len(partially_completed_applications) != 0 or all_servers_empty is False:
        processing_time += 1
        if processing_time > max_iterations + sec_per_day:
            print(f'ERROR: exceeding {max_iterations} iterations')
            quit()

        simulated_time_results.append(processing_time - sec_per_day)
        queue_results.append(len(applications))

        if diagnostics:
            print(f'Time = {processing_time - sec_per_day}')
            print(f'Queue Length: {len(applications)}')
            print(f'Partial: {len(partially_completed_applications)}')

        current_completed = complete_applications(edge_computing_systems, completed_applications, processing_time,
                                                  diagnostics)

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

        current_migrations = resume_applications(policy, location_distances, partially_completed_applications,
                                                 shortest_distances, delay_function, edge_computing_systems,
                                                 irradiance_list, processing_time, power_per_server,
                                                 degradable_applications, degradable_multiplier, diagnostics)

        current_migrations_results.append(current_migrations)
        if len(cumulative_migrations_results) == 0:
            cumulative_migrations_results.append(current_migrations)
        else:
            try:
                cumulative_migrations_results.append(cumulative_migrations_results[-1] + current_migrations)
            except TypeError:
                cumulative_migrations_results.append(current_migrations)

        if applications:
            start_applications(edge_computing_systems, applications, processing_time, global_applications,
                               degradable_applications, degradable_multiplier, diagnostics)

        if battery > 0:
            update_batteries(edge_computing_systems, power_per_server, irradiance_list, processing_time)

        all_servers_empty = get_applications_running(edge_computing_systems)  # check if applications are running

    processing_time -= sec_per_day  # started at t=86400
    simplify_time(processing_time)  # simulation time
    print(f'Execution Time: {time.time() - start_time}')  # end timer

    for app in completed_applications:
        total_overhead += app.overhead

    idle_rate = sum([app.overhead / (app.end_time - app.start_time) for app in completed_applications]) \
                / len(completed_applications)

    # write results to text file
    now = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
    with open(f'Outputs/{policy}_output_{now}.txt', 'w') as file:
        with open('config.txt', 'r') as config:
            reader = config.readlines()
        for line in reader:
            file.write(line)
            if line == 'Config\n':
                file.write(f"Nodes: {num_edges}\n")

        file.write('\n----------------\n')
        file.write("Completion Info\n")
        file.write(f"Total Simulated Time (seconds): {processing_time}\n")
        file.write(f"Total Overhead Time (seconds): {total_overhead}\n")
        file.write(f"Idle Rate: {idle_rate}")
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