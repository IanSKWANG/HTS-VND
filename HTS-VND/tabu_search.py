from deep_copy import deepcopy
from helpers import initialize, plot_itera
from tqdm import tqdm
from arg_parser import args

shake = None
if int(args.shake) == 1:
    shake = True
else:
    shake = False

class Tabu_search:

    def __init__(self, iter_max, tabu_table_length, data):
        self.tabu_table = []
        self.iter_max = iter_max
        self.tabu_table_length = tabu_table_length
        self.data = data

    def run(self):
        initial_solution = initialize(self.data)
        print("initial route is:", initial_solution.route)
        print("initial_service_time_of_station is:", initial_solution.service_time_of_station)
        print("initial unserviced_station is:", initial_solution.unserviced_station)
        print("initial profit is:", initial_solution.profit)
        initial_result = initial_solution.profit
        best_value_list = []
        best_value_list.append(initial_solution.profit)
        solution = initial_solution
        for i in tqdm(range(self.iter_max), ascii='░▒█'):
            if shake:
                solution_1 = deepcopy(solution)
                solution_2 = solution_1.shaking(self.data)
                best_neighbor = solution_2.VND(self.data, self.tabu_table)
            else:
                best_neighbor = solution.VND(self.data, self.tabu_table)
            if best_neighbor.route not in self.tabu_table:
                if best_neighbor.profit >= solution.profit:
                    solution = best_neighbor
                    # print("solution route is:", solution.route)
                    # print("solution profit is:", solution.profit)
                    best_value_list.append(solution.profit)
                    self.tabu_table.append(solution.route)
                else:
                    best_value_list.append(solution.profit)
                    pass
            elif best_neighbor.route in self.tabu_table:
                best_neighbor_of_best_neighbor = best_neighbor.VND(self.data, self.tabu_table)
                if best_neighbor_of_best_neighbor.profit >= solution.profit:
                    solution = best_neighbor_of_best_neighbor
                    best_value_list.append(solution.profit)
                else:
                    best_value_list.append(solution.profit)
                    pass
            while len(self.tabu_table) > self.tabu_table_length:
                self.tabu_table.pop(0)
            # self.tabu_table.append(solution.route)


        plot_itera(self.data, best_value_list)

        return solution, initial_result



