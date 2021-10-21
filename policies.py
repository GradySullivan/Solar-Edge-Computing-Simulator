import itertools
import math
import operator


def start_applications(edge_computing_systems, applications, shortest_distances):
    if applications is None:
        return
    powered_servers = [server for node in edge_computing_systems.keys() for server in node.servers if server.on is True]
    for server in powered_servers:
        for app in list(applications):
            if (app.memory <= server.memory) and (app.cores <= server.cores) and shortest_distances is None:
                server.start_application(app)
                applications.remove(app)
                print('started', app, 'from', app.parent, 'on', app.parent.parent)


def complete_applications(edge_computing_systems):
    powered_servers = [server for node in edge_computing_systems.keys() for server in node.servers if server.on is True]
    for server in powered_servers:
        for application in list(server.applications_running.keys()):
            application.time_left -= 1
            if application.time_left <= 0:
                server.stop_application(application)


def power_servers(edge_computing_systems):
    # determine which servers are on
    powered_servers = [server for edge in edge_computing_systems for server in edge.servers]
    for server in powered_servers:
        server.on = True


def shutdown_servers(edge_computing_systems, num_servers, power_per_server,
                     irradiance_list, processing_time, partially_completed_applications, applications):
    power_servers(edge_computing_systems)
    # turn off servers w/o enough power (priority to keep servers on that are closest to completing a task)
    for edge in edge_computing_systems.keys():
        servers_on = num_servers
        power = edge.get_power_generated(irradiance_list[processing_time][edge.index])  # update power available
        most_servers_on = math.floor(power / power_per_server)
        if most_servers_on < servers_on:  # determine how to shut down sites
            application_progression = []
            while most_servers_on < servers_on:
                for server in edge.servers:
                    try:
                        application_progression.append(min(list(server.applications_running.keys())))
                    except ValueError:
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
    return applications, partially_completed_applications


def resume_applications(edge_computing_systems, applications, shortest_distances):
    for app in applications:
        for server in shortest_distances[app.parent.parent][0].servers:
            if app.delay is None:
                app.delay = math.ceil(shortest_distances[server.parent][1] * .001)
                print('adding delay', app.delay)
            elif app.delay > 0:
                app.delay -= 1
            if app.delay <= 0 and server.on is True and app.cores <= server.cores and app.memory <= server.memory:
                print(f'resume app:{app}, from {app.parent.parent} to {server.parent}')
                server.start_application(app)
                applications.remove(app)
    return applications
