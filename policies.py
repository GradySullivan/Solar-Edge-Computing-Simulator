import itertools
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
    if applications is None:
        return
    powered_servers = [server for node in edge_computing_systems for server in node.servers if server.on is True]
    for server in powered_servers:
        for app in list(applications):
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
    powered_servers = [server for node in edge_computing_systems for server in node.servers if server.on is True]
    for server in powered_servers:
        for application in list(server.applications_running.keys()):
            application.time_left -= 1
            if application.time_left <= 0:
                server.stop_application(application)


def power_servers(edge_computing_systems: list):
    """

    :param edge_computing_systems: list of nodes
    :return: None
    """
    """Helper function that turns on all servers"""
    powered_servers = [server for edge in edge_computing_systems for server in edge.servers]
    for server in powered_servers:
        server.on = True


def shutdown_servers(edge_computing_systems: list, power_per_server: float, irradiance_list: list, processing_time: int,
                     partially_completed_applications: list):
    """

    :param edge_computing_systems: list of nodes
    :param power_per_server: power that each server needs to operate, in W
    :param irradiance_list: list of irradiance values for each node
    :param processing_time: simulated time, in seconds
    :param partially_completed_applications: list of applications that have been paused
    :return: partially_completed_applications (updated list of paused applications)
    """
    """Determines which servers to power off"""
    power_servers(edge_computing_systems)
    # turn off servers w/o enough power (priority to keep servers on that are closest to completing a task)
    for edge in edge_computing_systems:
        servers_on = len(edge.servers)
        power = edge.get_power_generated(irradiance_list[processing_time][edge.index])  # update power available
        most_servers_on = math.floor(power / power_per_server)
        if most_servers_on < servers_on:  # determine how to shut down sites
            application_progression = []
            while most_servers_on < servers_on:
                for server in edge.servers:
                    if server.applications_running.keys():
                        application_progression.append(min(list(server.applications_running.keys())))
                    else:
                        if server.on is True and server.applications_running == {}:
                            server.on = False
                            servers_on -= 1
                            if servers_on <= most_servers_on:
                                break
                if application_progression:
                    longest_app = max(application_progression, key=operator.attrgetter('time_left'))
                    longest_app.parent.on = False
                    servers_on -= 1
                    for app in list(longest_app.parent.applications_running):
                        longest_app.parent.stop_application(app)
                        application_progression.remove(app)
                        partially_completed_applications.insert(0, app)
                        print('pausing', app, app.time_left, 'on', app.parent.parent)
    return partially_completed_applications


def resume_applications(applications: list, shortest_distances: dict):
    """

    :param applications: list of applications
    :param shortest_distances: dictionary of (dictionary of node:(closest node,distance) pairs)
    :return: application (updated list of partially completed applications)
    """
    for app in applications:
        for server in shortest_distances[app.parent.parent][0].servers:
            if app.delay is None:
                app.delay = math.ceil(shortest_distances[server.parent][1] * .001)
            elif app.delay > 0:
                app.delay -= 1
            if app.delay <= 0 and server.on is True and app.cores <= server.cores and app.memory <= server.memory:
                print(f'resume app:{app}, from {app.parent.parent} to {server.parent}')
                server.start_application(app)
                applications.remove(app)
    return applications
