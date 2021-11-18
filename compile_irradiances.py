import os
import csv


def get_max_irradiance():
    # determine scaling
    lst = []
    for file in os.listdir('Irradiance Lists'):
        with open(f'Irradiance Lists/{file}', 'r') as f:
            lst2 = []
            reader = csv.reader(f, delimiter=',')
            next(reader)
            for line in reader:
                if line != '':
                    for i in range(1):
                        if float(line[2]) < 0:
                            lst2.append(float(0))
                        else:
                            lst2.append(float(line[2]) * 1)
                        if len(lst2) > 2000000:
                            break
            lst.append(lst2)
    max_list = []
    for i in lst:
        max_list.append(max(i[0:100]))
    return max(max_list)


def compile_irradiances(scale: float):
    lst = []
    for file in os.listdir('Irradiance Lists'):
        with open(f'Irradiance Lists/{file}', 'r') as f:
            lst2 = []
            reader = csv.reader(f, delimiter=',')
            next(reader)
            for line in reader:
                if line != '':
                    for i in range(3600):
                        if float(line[2]) < 0:
                            lst2.append(float(0))
                        else:
                            lst2.append(float(line[2]) * scale)
                        if len(lst2) > 5000000:
                            break
            lst.append(lst2)

    reformatted = []
    inner_len = min([len(i) for i in lst])
    for i in range(inner_len):
        temp = []
        for sublist in lst:
            temp.append(sublist[i])
        reformatted.append(temp)

    with open('irradiance.txt', 'w', newline='') as file:
        wr = csv.writer(file)
        file.write('irradiances\n')
        wr.writerows(reformatted)
