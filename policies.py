import math
import time
from operator import attrgetter


def start_applications(edge_computing_systems, applications, shortest_distances):
    for edge in edge_computing_systems.keys():  # for each edge computing site...
        for server in edge.servers:  # for each server in a particular edge site
            if server.on is True:
                for application in list(applications):  # for each application that still needs to run
                    if (application.memory <= server.memory) and (application.cores <= server.cores):
                        if application.parent is None:
                            print('start')
                            server.start_application(application)
                            applications.remove(application)  # remove from to-do list
                        elif application.parent.parent and shortest_distances is not None:
                            if server.parent == shortest_distances[edge][0]:  # application is transferring to new node
                                if application.delay is not None:
                                    if application.delay <= 0:
                                        print('delay over')
                                        server.start_application(application)
                                        application.delay = None
                                        applications.remove(application)
                                elif application.delay is None:
                                    print('transfer initiated')
                                    print(shortest_distances[edge][1])
                                    application.delay = math.ceil(shortest_distances[edge][1] * .001)
                                    print('delay = ', application.delay)
                        elif application.parent.parent == edge:  # application is resuming on same node
                            print('resume')
                            server.start_application(application)
                            applications.remove(application)


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


def shutdown_servers(edge_computing_systems, num_servers, power_per_server,
                     irradiance_list, processing_time, partially_completed_applications, applications):
    # determine which servers are on
    for edge in edge_computing_systems.keys():  # start by turning all servers back on
        for server in edge.servers:
            server.on = True
    # turn off servers w/o enough power (priority to keep servers on that are closest to completing a task)
    for edge in edge_computing_systems.keys():
        servers_on = num_servers
        power = edge.get_power_generated(irradiance_list[processing_time])  # update power available to edges
        most_servers_on = math.floor(power / power_per_server)
        if most_servers_on < servers_on:  # determine how to shut down sites
            application_progression = []
            while most_servers_on < servers_on:
                for server in edge.servers:
                    try:
                        application_progression.append(min(list(server.applications_running.keys())))
                    except:
                        if server.on is True and server.applications_running == {}:
                            server.on = False
                            servers_on -= 1
                            if servers_on <= most_servers_on:
                                break
                if application_progression:
                    longest_app = max(application_progression, key=attrgetter('time_left'))
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
