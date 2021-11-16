import os
import csv


if __name__ == '__main__':
    '''lst = []
    for file in os.listdir('processed'):
        with open(f'processed/{file}', 'r') as f:
            lst2 = []
            reader = csv.reader(f, delimiter=',')
            next(reader)
            for line in reader:
                if line != '':
                    for i in range(1):
                        if float(line[2]) < 0:
                            lst2.append(float(0))
                        else:
                            lst2.append(float(line[2]))
                        if len(lst2) > 50:
                            break
            lst.append(lst2)
    for i in lst:
        print(max(i[0:10]))
    quit()'''

    '''lst = []
    for file in os.listdir('processed'):
        print(file)
        with open(f'processed/{file}', 'r') as f:
            irr_tot = 0
            reader = csv.reader(f, delimiter=',')
            next(reader)
            for index, line in enumerate(reader):
                if line != '':
                    if float(line[2]) < 0:
                        pass
                    else:
                        irr_tot += float(line[2])
                    if index == 100:
                        break
            lst.append(irr_tot)
            print(irr_tot)
    quit()'''

    # determine scaling
    '''lst = []
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
    for i in lst:
        print(max(i[0:100]))
    quit()'''

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
                            lst2.append(float(line[2]) * 462.0044421) #6.160059228
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
