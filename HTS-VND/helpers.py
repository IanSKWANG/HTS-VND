import datetime
import sys
from random import random

import numpy as np
from matplotlib import pyplot as plt

from Data import Data
from Solution import Solution
from deep_copy import deepcopy


def initialize(data):
    solution = Solution(data.no_of_vehicles, data.no_of_stations)
    unserviced_station = list(range(1, data.no_of_stations + 1))
    for k in range(data.no_of_vehicles):
        solution.route[k].append(0)
    station_count = 0
    can_insert = [1 for _ in range(data.no_of_vehicles)]
    while sum(can_insert) != 0:
        current_vehicle = station_count % data.no_of_vehicles
        last_station = solution.route[current_vehicle][-1]
        next_station, service_time_of_station = pick_next_station(data, last_station, unserviced_station, solution.route[current_vehicle])
        if next_station == -1:
            can_insert[current_vehicle] = 0
            station_count +=1
            continue
        if next_station != -1:
            solution.route[current_vehicle].append(next_station)
            solution.service_time_of_station[current_vehicle].append(service_time_of_station)
            unserviced_station.remove(next_station)
            route_time = solution.get_route_time(data, solution.route[current_vehicle])
            if route_time > data.Tmax:
                solution.route[current_vehicle].pop()
                solution.service_time_of_station[current_vehicle].pop()
                unserviced_station.append(next_station)
                station_count += 1
                can_insert[current_vehicle] = 0
            else:
                station_count += 1

        if not unserviced_station:
            break
    for k in range(data.no_of_vehicles):
        # print(k)
        solution.route[k].append(0)
        solution.service_time_of_station[k].append(0)
        solution.service_time_of_station[k].insert(0, 0)
    solution.unserviced_station = unserviced_station
    initial_profit = solution.calculate_profit(data)
    solution.profit = initial_profit

    return solution


def pick_next_station(data, last_station, unserviced_station, route):
    station_with_largest_ratio = -1
    candidate = []
    candidate_wait_time = []
    new_route = deepcopy(route)
    for pick_station in unserviced_station:
        new_route.append(pick_station)
        arrival_time = get_arrival_time(data, new_route)
        if arrival_time <= data.cl[pick_station]:
            new_route.pop()
            candidate.append(pick_station)
            if arrival_time < data.op[pick_station]:
                waiting_time = data.op[pick_station] - arrival_time
                candidate_wait_time.append(waiting_time)
            else:
                waiting_time = 0
                candidate_wait_time.append(waiting_time)
        else:
            new_route.pop()
    if len(candidate) == 0:
        return -1, 0

    ratio_hp = 0
    for i in candidate:
        serial_number = candidate.index(i)
        time_consume = data.smin[last_station] + candidate_wait_time[serial_number] + data.time_matrix[last_station][
            i] + data.time_matrix[i][0] - data.time_matrix[last_station][0]
        ratio = np.power(data.Rate[i] * data.smin[i], 2) / time_consume
        if ratio > ratio_hp:
            ratio_hp = ratio
            station_with_largest_ratio = i
    next_station = station_with_largest_ratio
    service_time_of_station = data.smin[next_station]
    return next_station, service_time_of_station


def get_arrival_time(data, route):
    service_start_time = 0
    next_station_arrival_time = 0
    for i in range(len(route) - 1):
        last_station = route[i]
        next_station = route[i + 1]
        departure_time = service_start_time + data.smin[last_station]
        travel_time = data.time_matrix[last_station][next_station]
        next_station_arrival_time = departure_time + travel_time
        service_start_time = max(next_station_arrival_time, data.op[next_station])
    route_time_tillnow = next_station_arrival_time
    return route_time_tillnow

def plot_itera(data, best_value_list):
    plt.gca().get_yaxis().get_major_formatter().set_scientific(False)
    plt.plot(np.arange(1, len(best_value_list) + 1), best_value_list)
    plt.xlabel('Iterations')
    plt.ylabel('best value')
    plt.grid()
    plt.xlim(1, len(best_value_list) + 1)
    plt.savefig(f"data{data.dataset}/plots/{data.no_of_stations}_{data.no_of_vehicles}_{datetime.datetime.now()}.pdf", dpi=300)


