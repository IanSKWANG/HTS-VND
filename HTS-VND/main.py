import time
import datetime
from Data import Data
from tabu_search import Tabu_search
from arg_parser import args

if __name__ == '__main__':
    size = int(args.size)
    ntruck = int(args.ntruck)
    dataset = int(args.dataset)
    itermax = int(args.itermax)
    tabu_size = int(args.tabu_size)
    t = time.time()
    data = Data(no_of_stations=size, no_of_vehicles=ntruck, dataset=dataset)
    tabu = Tabu_search(iter_max=itermax, tabu_table_length=tabu_size, data=data)
    result, initial_result = tabu.run()
    running_time = time.time() - t
    file_name = open(f"data{data.dataset}/tabu_result_{data.no_of_stations}_{data.no_of_vehicles}_{datetime.datetime.now()}.txt", 'w')
    file_name.write(f"number of station = \t {data.no_of_stations}\n")
    file_name.write(f"number of UAV = \t {data.no_of_vehicles}\n")
    file_name.write(f"initial solution = \t {initial_result}\n")
    file_name.write(f"objective = \t {result.profit}\n")
    file_name.write(f"solve time = \t {running_time}\n")
    file_name.write(f"route = \t {result.route}\n")
    file_name.write(f"service time of station = \t {result.service_time_of_station}\n")
    file_name.write(f"iter_max = \t {tabu.iter_max}\n")
    file_name.write(f"tabu_table_length = \t {tabu.tabu_table_length}\n")
    print("running time is:", running_time)
    print("final unserviced station is:", result.unserviced_station)
    print("best_route is:", result.route)
    print("best_profit is:", result.profit)
    print("best_service_time_of_station is:", result.service_time_of_station)

