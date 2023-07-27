from deep_copy import deepcopy
from docplex.mp.model import Model
from Solution import Solution
from Data import Data

size = 100
ntruck = 1


data = Data(no_of_stations=size, no_of_vehicles=ntruck)
solution = Solution(data.no_of_vehicles, data.no_of_stations)
solution.route = [[0, 19, 5, 16, 2, 11, 37, 43, 42, 17, 31, 36, 40, 35, 24, 32, 0]]
# solution.service_time_of_station =[[0, 156, 151, 173, 143, 98, 148, 131, 167, 138, 169, 148, 182, 152, 146, 134, 98, 0], [0, 164, 144, 177, 152, 149, 142, 136, 136, 132, 128, 138, 96, 160, 150, 134, 0], [0, 148, 147, 148, 137, 147, 164, 141, 152, 139, 152, 141, 135, 99, 151, 142, 106, 0]]
# solution.if_route_feasible(data, solution.route, solution.service_time_of_station)
new_service_time_of_station = solution.find_best_service_time(data, solution.route, solution.service_time_of_station)

# print(new_service_time_of_station)

