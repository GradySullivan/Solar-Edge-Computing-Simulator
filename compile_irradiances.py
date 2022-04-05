import os
import csv
import time


def get_max_values():
    # determine scaling
    lst = []
    for file in os.listdir('Irradiance Lists'):
        with open(f'Irradiance Lists/{file}', 'r') as f:
            lst2 = []
            reader = csv.reader(f, delimiter=',')
            next(reader)
            next(reader)
            for line in reader:
                if line != '':
                    for i in range(1):
                        try:
                            if float(line[1]) < 0:
                                lst2.append(float(0))
                            else:
                                lst2.append(float(line[1]))
                        except ValueError:
                            lst2.append(0)
                        if len(lst2) > 50000000:
                            break
            lst.append((file, lst2))

    max_list = []
    for i in lst:
        max_list.append((i[0], max(i[1][0:864])))
    for index, value in enumerate(max_list):
        print(f'File: {value[0]}, Value: {value[1]}')


def compile_irradiances():
    data = []
    for file in os.listdir('Irradiance Lists'):
        with open(f'Irradiance Lists/{file}', 'r') as f:
            current_data = []
            reader = csv.reader(f, delimiter=',')
            next(reader)
            next(reader)
            for index, line in enumerate(reader):
                for _ in range(60):  # minute data
                    if line[1] == '' or float(line[1]) < 0:
                        current_data.append(float(0))
                    else:
                        current_data.append(float(line[1]))
        data.append(current_data)

    final_data = []
    min_len = min(map(len, data))

    for index in range(min_len):
        final_data.append([location[index] for location in data])

    with open('irradiance.txt', 'w', newline='') as file:
        wr = csv.writer(file)
        file.write('irradiances\n')
        wr.writerows(final_data)