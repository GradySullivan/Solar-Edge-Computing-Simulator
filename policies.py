import math
import operator


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
        for app in applications:
            '''To start an application, the server must have enough memory and cores. If this is fulfilled,
                an application will run based on the global_applications value. If true, applications are considered
                global and can start from any node. If false, applications must start from the a server whose node's 
                coordinates are first listed under "--- Node Locations --- '''
            if (app.memory <= server.memory) and (app.cores <= server.cores) and global_applications is True \
                    or (app.memory <= server.memory) and (app.cores <= server.cores) and global_applications is False \
                    and server.parent.index == 0:
                server.start_application(app)
                applications.remove(app)
                print('started', app, 'from', app.parent, 'on', app.parent.parent)


def complete_applications(edge_computing_systems: list):
    """

    :param edge_computing_systems: list of nodes
    :return: None
    """
    """Removes applications from servers once they finish running"""
    powered_servers = (server for node in edge_computing_systems for server in node.servers if server.on is True)
    for server in powered_servers:
        for application in server.applications_running:
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
        power = irradiance_list[processing_time][edge.index]#edge.get_power_generated(irradiance_list[processing_time][edge.index])  # update power available
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
                    shortest_apps.append(min(server.applications_running))
                for app in sorted(shortest_apps,
                                          key=operator.attrgetter('time_left'))[most_servers_on - servers_on:]:
                    app.parent.on = False
                    servers_on -= 1
                    max_power_available -= power_per_server
                    for running_app in app.parent.applications_running:
                        app.parent.stop_application(running_app)
                        shortest_apps.remove(running_app)
                        partially_completed_applications.insert(0, running_app)
                        print('pausing', running_app, running_app.time_left, 'on', running_app.parent.parent)


def resume_applications(applications: list, shortest_distances: dict, cost_multiplier: float):
    """

    :param applications: list of applications
    :param shortest_distances: dictionary of (dictionary of node:(closest node,distance) pairs)
    :param cost_multiplier: constant in calculating delay
    :return: None
    """
    for app in list(applications):
        print(app)
        if app.delay is None:
            app.delay = math.ceil(shortest_distances[app.parent.parent][1] * cost_multiplier)
        elif app.delay > 0:
            app.delay -= 1
        for server in shortest_distances[app.parent.parent][0].servers:
            print('i')
            if app.delay <= 0 and server.on is True and app.cores <= server.cores and app.memory <= server.memory:
                print(f'resume app:{app}, from {app.parent.parent} to {server.parent}')
                server.start_application(app)
                applications.remove(app)
                break


def update_batteries(edge_computing_systems: list, power_per_server: float, irradiance_list: tuple,
                     processing_time: int):
    """

    :param edge_computing_systems: list of nodes
    :param power_per_server: power each server consumes
    :param irradiance_list: tuple of solar irradiance lists
    :param processing_time: simulated time
    :return: None
    """
    """Adds power to node's battery if not used in this time period"""
    # power off servers without applications running
    for node in edge_computing_systems:
        for server in node.servers:
            if server.on is True and server.applications_running == {}:
                server.on = False

    # calculate leftover power per node
    for node in edge_computing_systems:
        power = irradiance_list[processing_time][node.index]#node.get_power_generated(irradiance_list[processing_time][node.index])  # update power available
        for server in node.servers:
            if server.on is True:
                power -= power_per_server
        if node.current_battery + power <= node.max_battery:
            node.current_battery += power
        else:
            node.current_battery = node.max_battery
        # print(f'Battery {node.index}: {node.current_battery}')
