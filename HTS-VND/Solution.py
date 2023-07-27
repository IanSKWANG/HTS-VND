import sys

from Data import Data
import random
from deep_copy import deepcopy
from docplex.mp.model import Model

class Solution:
    def __init__(self, no_of_vehicles, no_of_stations):
        self.no_of_vehicles = no_of_vehicles
        self.route = [[] for _ in range(no_of_vehicles)]
        self.profit = 0
        self.service_time_of_station = [[] for _ in range(no_of_vehicles)]
        self.unserviced_station = list(range(1, no_of_stations+1))

    def get_route_time(self, data, route):
        route.append(0)
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
        route.pop()
        return route_time_tillnow

    def get_new_route_time(self, data, route, service_time_of_station):
        route_time = 0
        service_start_time = 0
        next_station_arrival_time = 0
        for i in range(len(route) - 1):
            last_station = route[i]
            next_station = route[i + 1]
            departure_time = service_start_time + service_time_of_station[i]
            travel_time = data.time_matrix[last_station][next_station]
            next_station_arrival_time = departure_time + travel_time
            service_start_time = max(next_station_arrival_time, data.op[next_station])
        route_time = next_station_arrival_time

        return route_time

    def calculate_profit(self, data):
        profit = 0
        for k in range(self.no_of_vehicles):
            for i in self.route[k]:
                rate = data.Rate[i]
                service_time = self.service_time_of_station[k][self.route[k].index(i)]
                profit += rate * service_time
        self.profit = profit
        return profit


    def VND(self, data, tabu_list):
        j = 1
        ng_numbs = 0
        new_sol = Solution(self.no_of_vehicles, data.no_of_stations)
        for j in range(1,6):
            new_route, new_service_time_of_station, new_unserviced_station = self.localsearch(data, j, self.route, self.service_time_of_station, self.unserviced_station)
            new_sol.unserviced_station = new_unserviced_station
            new_sol.route = new_route
            new_sol.service_time_of_station = new_service_time_of_station
            new_sol.calculate_profit(data)
            if new_sol not in tabu_list:
                if new_sol.profit > self.profit:
                    self.route = new_sol.route
                    self.profit = new_sol.profit
                    self.service_time_of_station = new_sol.service_time_of_station
                    self.unserviced_station = new_sol.unserviced_station
                    j = 1
                else:
                    j += 1
        if new_sol.profit > self.profit and new_sol not in tabu_list:
            return new_sol
        else:
            return self

    def localsearch(self, data, j, route, service_time_of_station, unserviced_station):
        if j == 1:
            new_route, new_service_time_of_station, new_unserviced_station = self.insert(data, route, service_time_of_station, unserviced_station)
            return new_route, new_service_time_of_station, new_unserviced_station
        elif j == 2:
            new_route, new_service_time_of_station = self.opt2(data, route, service_time_of_station)
            return new_route, new_service_time_of_station, unserviced_station
        elif j == 3:
            new_route, new_service_time_of_station, new_unserviced_station = self.exchange(data, route, service_time_of_station, unserviced_station)
            return new_route, new_service_time_of_station, new_unserviced_station
        elif j == 4:
            new_route, new_service_time_of_station = self.cross(data, route, service_time_of_station)
            return new_route, new_service_time_of_station, unserviced_station
        # elif j == 5:
        #     new_route, new_service_time_of_station = self.prolong(data, route, service_time_of_station)
        #     return new_route, new_service_time_of_station, unserviced_station
        elif j == 5:
            new_route, new_service_time_of_station = self.find_best_service_time(data, route, service_time_of_station)
            return new_route, new_service_time_of_station, unserviced_station
        # elif j == 6:
        #     # add remove
        #     new_route, new_service_time_of_station, new_unserviced_station = self.remove_station(data, route, service_time_of_station, unserviced_station)
        #     return new_route, new_service_time_of_station, new_unserviced_station



    def if_route_feasible(self, data, route, service_time_of_station):
        # 判断路线是否可行
        for k in range(self.no_of_vehicles):
            if self.get_new_route_time(data, route[k], service_time_of_station[k]) > data.Tmax:
                return False
            service_start_time = 0
            for i in range(len(route[k])-1):
                last_station = route[k][i]
                next_station = route[k][i+1]
                departure_time = service_start_time + service_time_of_station[k][i]
                travel_time = data.time_matrix[last_station][next_station]
                next_station_arrival_time = departure_time + travel_time
                # print('next_station_arrival_time', next_station_arrival_time)
                # print(f"next station arrival time is {next_station_arrival_time}")
                service_start_time = max(next_station_arrival_time, data.op[next_station])
                if next_station_arrival_time > data.cl[next_station]:
                    return False
        # print("route is feasible")
        return True


    def insert(self, data, route, service_time_of_station, unserviced_station):
        # 插入操作
        # print("insert")
        # print(self.unserviced_station)
        if len(self.unserviced_station) == 0:
            return route, service_time_of_station, unserviced_station
        else:
            new_route = deepcopy(route)
            new_service_time_of_station = deepcopy(service_time_of_station)
            new_unserviced_station = deepcopy(unserviced_station)
            # print(f"{route} \n {service_time_of_station}")
            for k in range(self.no_of_vehicles):
                # 从未服务站点里随机选取一个站点
                station = random.choice(new_unserviced_station)
                # 从列表中随机选一个值出来
                for i in range(1, len(new_route[k])-1):
                    random_index = i
                    # 在随机选取的位置插入站点
                    new_route[k].insert(random_index, station)
                    # 计算插入站点后的服务时间
                    new_service_time_of_station[k].insert(random_index, data.smin[station])
                    # 判断插入后的路线是否可行
                    if self.if_route_feasible(data, new_route, new_service_time_of_station):
                        # 如果可行，将该站点从未服务站点列表中删除
                        # print("insert feasible")
                        new_unserviced_station.remove(station)
                        # print("insert success", new_unserviced_station)
                        return new_route, new_service_time_of_station, new_unserviced_station
                    else:
                        # print("insert failed")
                        # 不可行则回溯
                        new_route = deepcopy(route)
                        new_service_time_of_station = deepcopy(service_time_of_station)
                        new_unserviced_station = deepcopy(unserviced_station)
                        # print("insert fail", new_unserviced_station)
            return new_route, new_service_time_of_station, new_unserviced_station

    def swap(self, data, route, service_time_of_station):
        # 交换操作
        # print("swap")
        new_route = deepcopy(route)
        new_service_time_of_station = deepcopy(service_time_of_station)
        for k in range(self.no_of_vehicles):
            if len(new_route[k]) > 3:
            # 随机选取两个站点
            #     print(k)
            #     print(len(new_route[k]))
                station1_index = random.randint(1, len(new_route[k])-2)
                station2_index = random.randint(1, len(new_route[k])-2)
                # print(station1_index, station2_index)
                if station1_index != station2_index:
                    station1 = new_route[k][station1_index]
                    station2 = new_route[k][station2_index]
                    station1_service_time = new_service_time_of_station[k][station1_index]
                    station2_service_time = new_service_time_of_station[k][station2_index]
                    # 交换两个站点
                    new_route[k][station1_index] = station2
                    new_route[k][station2_index] = station1
                    # 交换对应的服务时间
                    new_service_time_of_station[k][station1_index] = station2_service_time
                    new_service_time_of_station[k][station2_index] = station1_service_time

                    # 判断交换后的路线是否可行
                    if self.if_route_feasible(data, new_route, new_service_time_of_station):
                        # print("swap fesaible")
                        # print(station1_index, station2_index)
                        # print(service_time_of_station[k][station1_index], service_time_of_station[k][station2_index])
                        # print(new_service_time_of_station[k][station1_index], new_service_time_of_station[k][station2_index])
                        return new_route, new_service_time_of_station
                    else:
                        # 不可行则回溯
                        new_route = route
                        new_service_time_of_station = service_time_of_station
            else:
                new_route = route
                new_service_time_of_station = service_time_of_station
        return new_route, new_service_time_of_station

    def exchange(self, data, route, service_time_of_station, unserviced_station):
        # 从unserviced_station中随机选取一个点，与route中的点交换
        # print("exchange")
        new_route = deepcopy(route)
        new_service_time_of_station = deepcopy(service_time_of_station)
        new_unserviced_station = deepcopy(unserviced_station)
        if len(new_unserviced_station) > 0:
            for k in range(self.no_of_vehicles):
                if len(new_route[k]) >= 3:
                    for i in new_unserviced_station:
                        # print("now i is", i)
                        # print("now unsercied station is", new_unserviced_station)
                        for n in new_route[k]:
                            exchange_station = i
                            # print("now exchange station is", exchange_station)
                            exchange_station_smax = data.smax[exchange_station]
                            old_station = n
                            # print("now old station is", old_station)
                            old_station_index = new_route[k].index(old_station)
                            if old_station != 0 :
                                # print("the old station is", old_station)
                                # print("the exchange station is", exchange_station)
                                new_route[k][old_station_index] = exchange_station
                                new_service_time_of_station[k][old_station_index] = exchange_station_smax
                                # print("exchange station is", exchange_station)
                                # print("unserviced station is", new_unserviced_station)
                                # 判断交换后的路线是否可行
                                if self.if_route_feasible(data, new_route, new_service_time_of_station):
                                    # print("exchange feasible")
                                    new_unserviced_station.remove(exchange_station)
                                    # print("after remove unserviced station is", new_unserviced_station)
                                    new_unserviced_station.append(old_station)
                                    # print("after append unserviced station is", new_unserviced_station)
                                    return new_route, new_service_time_of_station, new_unserviced_station
                                else:
                                    #换回之前状态
                                    new_route[k][old_station_index] = old_station
                                    new_service_time_of_station[k][old_station_index] = data.smin[old_station]
                            else:
                                pass



        return new_route, new_service_time_of_station, new_unserviced_station


    def cross(self, data, route, service_time_of_station):
        if len(route) == 1:
            return route, service_time_of_station
        else:
            new_route = deepcopy(route)
            new_service_time_of_station = deepcopy(service_time_of_station)
            route1 = random.choice(new_route)
            # print("route1 is", route1)
            route2 = random.choice(new_route)
            # print("route2 is", route2)
            while route1 == route2:
                route2 = random.choice(new_route)
            route1_index = new_route.index(route1)
            route2_index = new_route.index(route2)
            if len(route1) >= 3 and len(route2) >= 3:
                station1 = random.choice(route1)
                station2 = random.choice(route2)
                station1_index = route1.index(station1)
                station2_index = route2.index(station2)
                if station1 != 0 and station2 != 0:
                    route1[station1_index] = station2
                    route2[station2_index] = station1
                    new_service_time_of_station[route1_index][station1_index] = data.smin[station2]
                    new_service_time_of_station[route2_index][station2_index] = data.smin[station1]
                    # 判断交叉后的路线是否可行
                    if self.if_route_feasible(data, new_route, new_service_time_of_station):
                        # print("cross fesaible")
                        return new_route, new_service_time_of_station
                    else:
                        #交叉后不可行则回溯
                        new_route = deepcopy(route)
                        new_service_time_of_station = deepcopy(service_time_of_station)
                        return new_route, new_service_time_of_station
                else:
                    new_route = deepcopy(route)
                    new_service_time_of_station = deepcopy(service_time_of_station)
                    return new_route, new_service_time_of_station
            else:
                new_route = deepcopy(route)
                new_service_time_of_station = deepcopy(service_time_of_station)
                return new_route, new_service_time_of_station


    def opt2(self, data, route, service_time_of_station):
        #2-opt算法
        new_route = deepcopy(route)
        new_service_time_of_station = deepcopy(service_time_of_station)
        for k in range(self.no_of_vehicles):
            if len(new_route[k]) >= 5:
                for i in range(len(new_route[k]) - 2):
                    for j in range(i + 2, len(new_route[k]) - 1):
                        new_route[k][i + 1: j + 1] = new_route[k][j: i: -1]
                        new_service_time_of_station[k][i + 1: j + 1] = new_service_time_of_station[k][j: i: -1]
                        if self.if_route_feasible(data, new_route, new_service_time_of_station):
                            # print("opt2 fesaible")
                            return new_route, new_service_time_of_station
                        else:
                            new_route = deepcopy(route)
                            new_service_time_of_station = deepcopy(service_time_of_station)
                            return new_route, new_service_time_of_station
            else:
                return new_route, new_service_time_of_station



    def prolong(self, data, route, service_time_of_station):
        new_route = deepcopy(route)
        new_service_time_of_station = deepcopy(service_time_of_station)
        for k in range(self.no_of_vehicles):
            for i in range(len(new_route[k])):
                station = new_route[k][i]
                station_st = new_service_time_of_station[k][i]
                if station_st == data.smax[station]:
                    i += 1
                else:
                    new_service_time_of_station[k][i] = data.smax[station]
                    if self.if_route_feasible(data, new_route, new_service_time_of_station):
                        # print("prolong feasible")
                        service_time_of_station[k] = new_service_time_of_station[k]
                    else:
                        while not self.if_route_feasible(data, new_route, new_service_time_of_station) and new_service_time_of_station[k][i] > data.smin[station]:
                            new_service_time_of_station[k][i] -= 1
        return route, service_time_of_station

    def remove_station(self, data, route, service_time_of_station, unserviced_station):
        # 从route中随机选取一个点，将其移除
        # print("remove")
        new_route = deepcopy(route)
        new_service_time_of_station = deepcopy(service_time_of_station)
        new_unserviced_station = deepcopy(unserviced_station)
        for k in range(self.no_of_vehicles):
            if len(new_route[k]) >= 3:
                station = random.choice(new_route[k])
                station_index = new_route[k].index(station)
                station_st = new_service_time_of_station[k][station_index]
                if station != 0:
                    new_route[k].remove(station)
                    del new_service_time_of_station[k][station_index]
                    # 判断移除后的路线是否可行
                    if self.if_route_feasible(data, new_route, new_service_time_of_station):
                        # print("fesaible")
                        new_unserviced_station.append(station)
                        return new_route, new_service_time_of_station, new_unserviced_station
                    else:
                        # 移除后不可行则回溯
                        # print("before", new_route[k])
                        new_route[k].insert(station_index, station)
                        # print("after", new_route[k])
                        # print("before", new_service_time_of_station[k])
                        new_service_time_of_station[k].insert(station_index, service_time_of_station[k][station_index])
                        # print("after", new_service_time_of_station[k])

        return new_route, new_service_time_of_station, new_unserviced_station

    def shaking(self, data):
        solution = deepcopy(self)
        route = deepcopy(self.route)
        service_time_of_station = deepcopy(self.service_time_of_station)
        unserviced_station = deepcopy(self.unserviced_station)
        new_route, new_service_time_of_station, new_unserviced_station = self.remove_station(data, route, service_time_of_station, unserviced_station)
        new_route, new_service_time_of_station = self.cross(data, new_route, new_service_time_of_station)
        new_route, new_service_time_of_station = self.opt2(data, new_route, new_service_time_of_station)
        # new_route, new_service_time_of_station, new_unserviced_station = self.exchange(data, new_route, new_service_time_of_station, new_unserviced_station)
        solution.route = new_route
        solution.service_time_of_station = new_service_time_of_station
        solution.unserviced_station = new_unserviced_station
        solution.calculate_profit(data)

        return solution

    def find_best_service_time(self, data, route, service_time_of_station):
        route = deepcopy(route)
        service_time_of_station = deepcopy(service_time_of_station)
        smin = data.smin
        smax = data.smax
        op = data.op
        cl = data.cl
        Tmax = 2880
        time_matrix = data.time_matrix
        new_service_time_of_station = []
        for k in range(self.no_of_vehicles):
            new_service_time_of_station.append([])
            smin_r = []
            smax_r = []
            op_r = []
            cl_r = []
            for i in range(len(route[k])):
                smin_r.append(smin[route[k][i]])
                smax_r.append(smax[route[k][i]])
                op_r.append(op[route[k][i]])
                cl_r.append(cl[route[k][i]])
            N = [i for i in range(len(route[k]))]
            n = len(N)
            arrival_time = [(i) for i in N ]
            service_time = [(i) for i in N ]
            A = [(i,j) for i in N for j in N if i != j]
            travel_time = {(i,j):0 for i,j in A}
            for i,j in A:
                # print(i,j)
                travel_time[(i,j)] = time_matrix[route[k][i],route[k][j]]

            mdl = Model("best_service_time")

            s = mdl.continuous_var_list(service_time, name = "s")
            a = mdl.continuous_var_list(arrival_time, name = "a")

            mdl.maximize(mdl.sum(s[i] for i in N))

            mdl.add_constraint(s[0] == 0)
            mdl.add_constraint(s[n-1] == 0)
            mdl.add_constraints(s[i] >= smin_r[i] for i in N)
            mdl.add_constraints(s[i] <= smax_r[i] for i in N)
            mdl.add_constraints(a[i] <= cl_r[i] for i in N)
            mdl.add_constraints(a[i] >= a[i-1] + s[i-1] + travel_time[(i-1,i)] for i in N[1:])
            mdl.add_constraint(a[0] == 0)
            mdl.add_constraint(a[n-1]+s[n-1]+travel_time[n-1,0] <= Tmax)

            mdl.set_time_limit(60)
            sol = mdl.solve(log_output = False)
            # print(sol.objective_value)
            if sol is None:
                new_service_time_of_station[k] = deepcopy(service_time_of_station[k])
                continue
            # 把新的服务时间赋值给service_time_of_station
            for i in range(n):
                new_service_time_of_station[k].append(sol.get_value(s[i]))
                # print(sol.get_value(s[i]))
                # print(i, sol.get_value(a[i]))
        # print("new_service_time_of_station", new_service_time_of_station)
        return route, new_service_time_of_station






















