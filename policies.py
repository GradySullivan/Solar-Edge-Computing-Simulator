import math
import operator

from setup import *


def start_applications(edge_computing_systems: list, applications: list, global_applications: bool):
    """
    :param edge_computing_systems: list of nodes
    :param applications: list of applications
    :param global_applications: determines if applications can start at any server or not
    :return: None
    """
    """Start applications on a server for the first time"""
    powered_servers = (server for node in edge_computing_systems for server in node.servers if server.on is True)
    for server in powered_servers:
        if server.cores > 0 and server.memory > 0:
            for app in list(applications):
                '''To start an application, the server must have enough memory and cores. If this is fulfilled,
                    an application will run based on the global_applications value. If true, applications are considered
                    global and can start from any node. If false, applications must start from the a server whose node's 
                    coordinates are first listed under "--- Node Locations ---" '''
                if (app.memory <= server.memory) and (app.cores <= server.cores) and global_applications is True \
                        or (app.memory <= server.memory) and (app.cores <= server.cores) and global_applications is False \
                        and server.parent.index == 0:
                    server.start_application(app)
                    applications.remove(app)
                    #print('started', app, 'from', app.parent, 'on', app.parent.parent)


def complete_applications(edge_computing_systems: list):
    """
    :param edge_computing_systems: list of nodes
    :return: None
    """
    """Removes applications from servers once they finish running"""
    powered_servers = (server for node in edge_computing_systems for server in node.servers if server.on is True)
    for server in powered_servers:
        for application in list(server.applications_running):
            application.time_left -= 1
            if application.time_left <= 0:
                server.stop_application(application)


def power_servers(edge_computing_systems: list):
    """
    :param edge_computing_systems: list of nodes
    :return: None
    """
    """Helper function that turns on all servers"""
    powered_servers = (server for edge in edge_computing_systems for server in edge.servers)
    for server in powered_servers:
        server.on = True


def shutdown_servers(edge_computing_systems: list, power_per_server: float, irradiance_list: tuple,
                     processing_time: int, partially_completed_applications: list):
    """
    :param edge_computing_systems: list of nodes
    :param power_per_server: power that each server needs to operate, in W
    :param irradiance_list: tuple of irradiance values for each node
    :param processing_time: simulated time, in seconds
    :param partially_completed_applications: list of applications that have been paused
    :return: None
    """
    """Determines which servers to power off"""
    power_servers(edge_computing_systems)
    # turn off servers w/o enough power (priority to keep servers on that are closest to completing a task)
    for edge in edge_computing_systems:
        servers_on = len(edge.servers)
        power = edge.get_power_generated(irradiance_list[processing_time][edge.index])  # update power available
        battery_power = edge.current_battery
        max_power_available = power + battery_power
        most_servers_on = math.floor((power + battery_power) / power_per_server)

        '''print(f'Power {edge.index}: {power}')
        #print(f'Batter Power: {battery_power}')
        #print(f'Max Power: {max_power_available}')
        print(f'Servers on: {servers_on}')
        print(f'Most Servers on: {most_servers_on}')'''

        if servers_on > most_servers_on:
            shortest_apps = []
            for server in edge.servers:
                if not server.applications_running and server.on is True:
                    server.on = False
                    servers_on -= 1
                    max_power_available -= power_per_server
                    if servers_on <= most_servers_on:
                        break
                else:
                    shortest_apps.append(min(server.applications_running, key=operator.attrgetter('time_left')))
            for app in sorted(shortest_apps,
                              key=operator.attrgetter('time_left'))[most_servers_on - servers_on:]:
                app.parent.on = False
                servers_on -= 1
                max_power_available -= power_per_server
                shortest_apps.remove(app)
                for running_app in app.parent.applications_running:
                    app.parent.stop_application(running_app)
                    partially_completed_applications.insert(0, running_app)
                    #print('pausing', running_app, running_app.time_left, 'on', running_app.parent.parent)


def resume_applications(policy: str, applications: list, shortest_distances: dict, cost_multiplier: float,
                        edge_computing_systems: list, irradiance_list: list, processing_time: int,
                        power_per_server: float):
    """
    :param policy: decides which task transfer policy to use
    :param applications: list of applications
    :param shortest_distances: dictionary of (dictionary of node:(closest node,distance) pairs)
    :param cost_multiplier: constant in calculating delay
    :param edge_computing_systems: list of all edge sites that are part of the edge computing system
    :param irradiance_list: list of solar irradiance tuples
    :param processing_time: simulated time
    :param power_per_server: power each server consumes
    :return: None
    """
    def passive():
        for app in list(applications):
            if app.parent.on and app.cores <= app.parent.cores and app.memory <= app.parent.memory:
                app.parent.start_application(app)
                app.delay = None
                applications.remove(app)

    def greedy():
        location_distances = get_distances(edge_computing_systems)
        for app in list(applications):
            if app.delay is None:
                options = []
                # print(f'START: {app.parent.parent.index}')
                for node in edge_computing_systems:
                    power = node.get_power_generated(irradiance_list[processing_time][node.index])
                    if app.parent.parent == node:
                        delay = 0
                    else:
                        try:
                            delay = math.ceil(location_distances[(app.parent.parent, node)] * cost_multiplier)
                        except KeyError:
                            delay = math.ceil(location_distances[(node, app.parent.parent)] * cost_multiplier)
                    if delay == 0:
                        options.append((power, delay, node, 'wait'))
                    else:
                        options.append((power, delay, node, 'transfer'))
                # print(options)
                best_choice = min(options, key=lambda n: n[1])
                # print(best_choice)
                app.delay = best_choice[1]
                app.parent = best_choice[2].servers[0]
                # print(f'END: {app.parent.parent.index}')
            elif app.delay > 0:
                app.delay -= 1
            if app.delay <= 0:
                for server in app.parent.parent.servers:
                    if server.on is True and app.cores <= server.cores and app.memory <= server.memory:
                        # print(f'resume app:{app} on {server.parent}')
                        server.start_application(app)
                        app.delay = None
                        applications.remove(app)
                        break

    def super_greedy():
        location_distances = get_distances(edge_computing_systems)
        for app in list(applications):
            if app.delay is None:
                options = []
                # print(f'START: {app.parent.parent.index}')
                for node in edge_computing_systems:
                    power = node.get_power_generated(irradiance_list[processing_time][node.index])
                    if app.parent.parent == node:
                        delay = 0
                    else:
                        try:
                            delay = math.ceil(location_distances[(app.parent.parent, node)] * cost_multiplier)
                        except KeyError:
                            delay = math.ceil(location_distances[(node, app.parent.parent)] * cost_multiplier)
                    if delay == 0:
                        options.append((power, delay, node, 'wait'))
                    else:
                        options.append((power, delay, node, 'transfer'))
                # print(options)
                best_choice = max(options, key=lambda n: (n[0], -n[1]))
                # print(best_choice)
                app.delay = best_choice[1]
                app.parent = best_choice[2].servers[0]
                # print(f'END: {app.parent.parent.index}')
            elif app.delay > 0:
                app.delay -= 1
            if app.delay <= 0:
                for server in app.parent.parent.servers:
                    if server.on is True and app.cores <= server.cores and app.memory <= server.memory:
                        # print(f'resume app:{app} on {server.parent}')
                        server.start_application(app)
                        app.delay = None
                        applications.remove(app)
                        break

    def yolo():
        for app in list(applications):
            if app.delay is None:
                app.delay = math.ceil(shortest_distances[app.parent.parent][1] * cost_multiplier)
            elif app.delay > 0:
                app.delay -= 1
            if app.delay <= 0:
                for server in shortest_distances[app.parent.parent][0].servers:
                    if server.on is True and app.cores <= server.cores and app.memory <= server.memory:
                        print(f'resume app:{app}, from {app.parent.parent} to {server.parent}')
                        server.start_application(app)
                        app.delay = None
                        applications.remove(app)
                        break

    def look_ahead():
        location_distances = get_distances(edge_computing_systems)
        for app in list(applications):
            if app.delay is None:
                # print(f'ORIGINAL: {app.parent.parent} {app.parent.parent.index}')
                options = []
                for node in edge_computing_systems:
                    if node == app.parent.parent:
                        delay = 0
                    else:
                        try:
                            delay = math.ceil(location_distances[(app.parent.parent, node)] * cost_multiplier)
                        except KeyError:
                            delay = math.ceil(location_distances[(node, app.parent.parent)] * cost_multiplier)
                    # print(f'DELAY: {delay} --> Node {node.index}')
                    future_processing_time = processing_time + delay
                    while True:
                        power = irradiance_list[future_processing_time][
                            node.index]  # node.get_power_generated(irradiance_list[processing_time][node.index])  # update power available
                        if power >= power_per_server:
                            if app.parent.parent == node:
                                options.append((power, future_processing_time - processing_time, node.index, 'wait'))
                            else:
                                options.append((power, future_processing_time - processing_time, node.index,
                                                'transfer'))
                        future_processing_time += 1
                        if power >= power_per_server:
                            break
                min_delay = min(options, key=lambda n: (n[1], -n[0]))[1]
                better_options = [choice for index, choice in enumerate(options) if choice[1] == min_delay]
                for index, option in enumerate(better_options):
                    if index == 0:
                        best_choice = option
                    if option[3] == 'wait':
                        best_choice = option
                app.delay = best_choice[1]
                app.parent = edge_computing_systems[best_choice[2]].servers[0]
                # print(f'NEW: {app.parent.parent.index}')
            else:
                if app.delay > 0:
                    app.delay -= 1
                if app.delay <= 0:
                    for server in app.parent.parent.servers:
                        if server.on and app.cores <= server.cores and app.memory <= server.memory:
                            server.start_application(app)
                            # print(f'resume app:{app} on {server.parent}')
                            app.parent = server
                            app.delay = None
                            applications.remove(app)
                            break

    def practical():
        location_distances = get_distances(edge_computing_systems)
        for app in list(applications):
            if app.delay is None:
                # print(f'ORIGINAL: {app.parent.parent} {app.parent.parent.index}')
                options = []
                for node in edge_computing_systems:
                    if node == app.parent.parent:
                        delay = 0
                    else:
                        try:
                            delay = math.ceil(location_distances[(app.parent.parent, node)] * cost_multiplier)
                        except KeyError:
                            delay = math.ceil(location_distances[(node, app.parent.parent)] * cost_multiplier)
                    yesterday_irradiance1 = [value[node.index] for index, value in enumerate(irradiance_list)
                                             if processing_time - 90000 < index < processing_time - 86400]
                    yesterday_irradiance2 = [value[node.index] for index, value in enumerate(irradiance_list)
                                             if processing_time - 86400 < index < processing_time - 82600]
                    today_irradiance1 = [value[node.index] for index, value in enumerate(irradiance_list)
                                         if processing_time - 3600 < index < processing_time]
                    if len(yesterday_irradiance1) > 0:
                        avg_yesterday_irradiance1 = sum(yesterday_irradiance1) / len(yesterday_irradiance1)
                    else:
                        avg_yesterday_irradiance1 = 1000
                    if len(yesterday_irradiance2) > 0:
                        avg_yesterday_irradiance2 = sum(yesterday_irradiance2) / len(yesterday_irradiance2)
                    else:
                        avg_yesterday_irradiance2 = 1000
                    if len(today_irradiance1) > 0:
                        avg_today_irradiance1 = sum(today_irradiance1) / len(today_irradiance1)
                    else:
                        avg_today_irradiance1 = sum(today_irradiance1) / len(today_irradiance1)
                    irradiance = avg_yesterday_irradiance2 * avg_today_irradiance1 / avg_yesterday_irradiance1
                    estimated_power = node.get_power_generated(irradiance)
                    if estimated_power >= power_per_server:
                        if app.parent.parent == node:
                            options.append((estimated_power, delay, node.index, 'wait'))
                        else:
                            options.append((estimated_power, delay, node.index, 'transfer'))
                min_delay = min(options, key=lambda n: (n[1], -n[0]))[1]
                better_options = [choice for index, choice in enumerate(options) if choice[1] == min_delay]
                for index, option in enumerate(better_options):
                    if index == 0:
                        best_choice = option
                    if option[3] == 'wait':
                        best_choice = option
                app.delay = 2  # best_choice[1]
                app.parent = edge_computing_systems[0].servers[0]  # edge_computing_systems[best_choice[2]].servers[0]
                # print(f'NEW: {app.parent.parent.index}')
            elif app.delay > 0:
                app.delay -= 1
            if app.delay <= 0:
                for server in app.parent.parent.servers:
                    if server.on and app.cores <= server.cores and app.memory <= server.memory:
                        server.start_application(app)
                        # print(f'resume app:{app} on {server.parent} {server.parent.index}')
                        app.parent = server
                        app.delay = None
                        applications.remove(app)
                        break

    if policy == 'YOLO':
        yolo()
    elif policy == 'passive':
        passive()
    elif policy == 'super-greedy':
        super_greedy()
    elif policy == 'greedy':
        greedy()
    elif policy == 'look-ahead':
        look_ahead()
    elif policy == 'practical':
        practical()


def update_batteries(edge_computing_systems: list, power_per_server: float, irradiance_list: tuple,
                     processing_time: int):
    """
    :param edge_computing_systems: list of nodes
    :param power_per_server: power each server consumes
    :param irradiance_list: list of solar irradiance tuples
    :param processing_time: simulated time
    :return: None
    """
    """Adds power to node's battery if not used in this time period"""
    # power off servers without applications running
    for node in edge_computing_systems:
        for server in node.servers:
            if server.on is True and not server.applications_running:
                server.on = False

    # calculate leftover power per node
    for node in edge_computing_systems:
        power = node.get_power_generated(irradiance_list[processing_time][node.index])  # update power available
        for server in node.servers:
            if server.on is True:
                power -= power_per_server
        if node.current_battery + power <= node.max_battery:
            node.current_battery += power
        else:
            node.current_battery = node.max_battery
        #print(f'Battery {node.index}: {node.current_battery}')
