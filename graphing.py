import matplotlib.pyplot as plt
import os
import csv
import numpy as np


class Results:
    def __init__(self, policy: str, simulated_time: list, queue: list, current_paused_applications: list,
                 cumulative_paused_applications: list, current_migrations: list, cumulative_migrations: list,
                 cumulative_completion:list, completion_rate: list, completion_location_counts: list):
        self.policy = policy
        self.simulated = simulated_time
        self.queue = queue
        self.current_paused = current_paused_applications
        self.cumulative_paused = cumulative_paused_applications
        self.current_migrations = current_migrations
        self.cumulative_migrations = cumulative_migrations
        self.cumulative_completion = cumulative_completion
        self.completion_rate = completion_rate
        self.total_time = simulated_time[-1]
        self.location_counts = completion_location_counts


if __name__ == '__main__':
    outputs = []
    for file in os.listdir('Outputs'):
        simulated_time = []
        queue = []
        current_paused_applications = []
        cumulative_paused_applications = []
        current_migrations = []
        cumulative_migrations = []
        cumulative_completion = []
        completion_rate = []
        completion_location_counts = []

        with open(f'Outputs/{file}', 'r') as f:
            counter = False
            reader = csv.reader(f, delimiter=':')
            for index, line in enumerate(reader):
                print(line)
                if line[0] == 'Policy':
                    policy = line[1].strip()
                elif line[0] == 'Application Completion Locations':
                    counter = True
                elif counter:
                    if line[0] == '----------------':
                        counter = False
                    else:
                        completion_location_counts.append(int(line[1]))
                elif index > 30:
                    print(index)
                    break

        with open(f'Outputs/{file}', 'r') as f:
            reader = csv.reader(f, delimiter=',')
            start = False
            for index, line in enumerate(reader):
                if line[0] == 'Simulated Time':
                    start = True
                elif start:
                    simulated_time.append(int(line[0]))
                    queue.append(int(line[1]))
                    current_paused_applications.append(int(line[2]))
                    cumulative_paused_applications.append(int(line[3]))
                    current_migrations.append(int(line[4]))
                    cumulative_migrations.append(int(line[5]))
                    cumulative_completion.append(int(line[6]))
                    completion_rate.append(float(line[7]))
                elif index > 100:
                    break

        outputs.append(Results(policy, simulated_time, queue, current_paused_applications, cumulative_paused_applications,
                               current_migrations, cumulative_migrations, cumulative_completion, completion_rate,
                               completion_location_counts))

    for output in outputs:
        print(output.policy, output.total_time)

    # methods vs simulated time
    '''methods = [output.policy for output in outputs]
    sim_time = [output.total_time for output in outputs]
    plt.figure(figsize=(5, 3))
    for index, value in enumerate(sim_time):
        plt.text(index, value, str(value), color='black')
    plt.bar(methods, sim_time, color='gray', width=0.5)
    plt.ylabel('Simulated Time (s)')
    #plt.ticklabel_format(axis='y', style='plain')
    plt.show()'''

    # methods vs completion locations
    node0, node1, node2 = [], [], []
    for output in outputs:
        node0.append(output.location_counts[0])
        node1.append(output.location_counts[1])
        node2.append(output.location_counts[2])
    print(node0, node1, node2)

    N = 6
    ind = np.arange(N)
    width = 0.25

    bar1 = plt.bar(ind, node0, width, color='r')
    bar2 = plt.bar(ind + width, node1, width, color='g')
    bar3 = plt.bar(ind + width * 2, node2, width, color='b')

    plt.xlabel("Methods")
    plt.ylabel('Tasks Completed')

    plt.xticks(ind + width, ['greedy', 'look-ahead', 'passive', 'practical', 'super-greedy', 'YOLO'])
    plt.legend((bar1, bar2, bar3), ('Node 0', 'Node 1', 'Node 2'))
    plt.show()
