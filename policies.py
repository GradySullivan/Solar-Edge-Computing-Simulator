import math
from operator import attrgetter


def start_applications(edge_computing_systems, applications):
    for edge in edge_computing_systems.keys():  # for each edge computing site...
        for server in edge.servers:  # for each server in a particular edge site
            if server.on is True:
                for application in list(applications):  # for each application that still needs to run
                    if (application.memory <= server.memory) and (application.cores <= server.cores):
                        server.start_application(application)
                        applications.remove(application)  # remove from to-do list


def complete_applications(edge_computing_systems):
    for edge in edge_computing_systems.keys():  # for each edge computing site...
        for server in edge.servers:  # for each server in a particular edge site
            if server.on is True:
                for application in list(server.applications_running.keys()):  # for each application running...
                    # print(application, 'Time Left', application.time_left)
                    if application.time_left <= 0:
                        server.stop_application(application)


def shutdown_servers(edge_computing_systems, partially_completed_applications, num_servers, power_per_server,
                     irradiance_list, processing_time, applications):
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
                    for app in list(server.applications_running.keys()):
                        application_progression.append(app)
                if application_progression:
                    longest_app = max(application_progression, key=attrgetter('time_left'))
                min_server = longest_app.parent
                min_server.on = False
                for app in list(min_server.applications_running.keys()):
                    application_progression.remove(app)
                servers_on -= 1
                print('paused')

    return applications