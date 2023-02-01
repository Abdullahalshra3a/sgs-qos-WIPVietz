import csv
from os import listdir
import numpy as np
from sklearn.metrics import mean_absolute_error

def objective_function(target, candidate_schedules):
    sum_cs = np.zeros(len(target))
    for agent in candidate_schedules:
        schedule = np.array(candidate_schedules[agent]).astype(np.float)
        sum_cs = np.add(schedule, sum_cs)
    return mean_absolute_error(target, sum_cs)

def read_files():
    file_list = listdir("../isaac_standalone/schedules")
    #print(file_list)
    flexibilties = {}
    for filename in file_list:
        schedules = []
        with open("../isaac_standalone/schedules/" + filename, newline='') as csvfile:
             schedules_csv = csv.reader(csvfile, delimiter=' ', quotechar='|')
             for row in schedules_csv:
                 schedules.append(row)
                 #print(', '.join(row))

        flexibilties[filename] = schedules
    return flexibilties


flexibilities = read_files()
target = [600.0, 400., 400., 400.]
num_schedules = len(list(flexibilities.values())[0])
print(num_schedules)
candidate = {}
for agent in flexibilities:
    candidate[agent] = flexibilities[agent][0]
error = objective_function(target, candidate)
print(error)

