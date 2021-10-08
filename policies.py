import math


def start_applications(edge_computing_systems, applications):
    for edge in edge_computing_systems.keys():  # for each edge computing site...
        for server in edge.servers:  # for each server in a particular edge site
            if server.on is True:
                for application in list(applications):  # for each application that still needs to run
                    if (application.memory <= server.memory) and (application.cores <= server.cores):
                        server.start_application(application)
                        applications.remove(application)  # remove from to-do list


def complete_applications(edge_computing_systems):
    processing = []
    for edge in edge_computing_systems.keys():  # for each edge computing site...
        for server in edge.servers:  # for each server in a particular edge site
            if server.on is True:
                for application in list(server.applications_running.keys()):  # for each application running...
                    if application not in processing:  # if the application wasn't added in this time iteration...
                        application.time_left -= 1
                        # print(application, 'Time Left', application.time_left)
                        if application.time_left <= 0:
                            server.stop_application(application)
                        processing.append(application)  # to prevent application decrementing multiple times


def shutdown_servers(edge_computing_systems, partially_completed_applications, num_servers, power_per_server,
                     irradiance_list, processing_time):
    # determine which servers are on
    for edge in edge_computing_systems.keys():  # start by turning all servers back on
        for server in edge.servers:
            server.on = True
    server_power_updated = False

    # turn off servers w/o enough power (priority to keep servers on that are closest to completing a task)
    while server_power_updated is False:
        for edge in edge_computing_systems.keys():
            servers_on = num_servers
            power = edge.get_power_generated(irradiance_list[processing_time])  # update power available to edges
            if power == 0:  # turn off all servers if no power
                print('shutting down all servers')
                for server in edge.servers:
                    server.on = False
                server_power_updated = True
            elif power / servers_on < power_per_server:  # determine how to shut down sites
                application_progression = {}
                while power / servers_on < power_per_server and servers_on > 0:
                    for server in edge.servers:
                        if server.applications_running == {}:
                            server.on = False
                            servers_on -= 1
                            break
                        application_progression[server] = max(server.applications_running).time_left
                    if application_progression != {}:
                        min_server = max(application_progression, key=application_progression.get)
                        min_server.on = False
                        del application_progression[min_server]
                        servers_on -= 1
                server_power_updated = True
            else:
                server_power_updated = True
    return partially_completed_applications
