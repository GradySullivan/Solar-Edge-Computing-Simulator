import math
import operator


def start_applications(edge_computing_systems, applications, shortest_distances):
    powered_servers = [server for node in edge_computing_systems.keys() for server in node.servers if server.on is True]
    for server in powered_servers:
        for app in list(applications):
            if (app.memory <= server.memory) and (app.cores <= server.cores) and shortest_distances is None:
                if shortest_distances is None:  # new applications
                    server.start_application(app)
                    applications.remove(app)
            elif (app.memory <= server.memory) and (app.cores <= server.cores) and shortest_distances is not None:
                #  partially completed applications
                print('PARTIALLY COMPLETED')
                if app.parent.parent == server.parent:  # resume running from same node
                    server.start_application(app)
                    applications.remove(app)
                    print('RESUME')
                elif app.parent.parent == shortest_distances[server.parent][1]:
                    if app.delay is None:
                        print('TRANSMITTING')
                        app.delay = math.ceil(shortest_distances[server.parent][1] * .001)
                    elif app.delay <= 0:
                        print('ARRIVED')
                        server.start_application(app)
                        app.delay = None


def complete_applications(edge_computing_systems):
    powered_servers = [server for node in edge_computing_systems.keys() for server in node.servers if server.on is True]
    for server in powered_servers:
        for application in list(server.applications_running.keys()):
            application.time_left -= 1
            if application.time_left <= 0:
                server.stop_application(application)


def shutdown_servers(edge_computing_systems, num_servers, power_per_server,
                     irradiance_list, processing_time, partially_completed_applications, applications):
    # determine which servers are on
    powered_servers = [server for edge in edge_computing_systems for server in edge.servers]
    for server in powered_servers:
        server.on = True
    # turn off servers w/o enough power (priority to keep servers on that are closest to completing a task)
    for edge in edge_computing_systems.keys():
        servers_on = num_servers
        #power = edge.get_power_generated(irradiance_list[processing_time])  # update power available to edges
        power = edge.get_power_generated(irradiance_list[0])
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
    return applications, partially_completed_applications


def decrement_transfer_time(partially_completed_applications):
    for application in partially_completed_applications:
        if application.delay is not None:
            application.delay -= 1
    return partially_completed_applications
