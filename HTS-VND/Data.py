import pandas as pd

class Data:
    def __init__(self, no_of_stations, no_of_vehicles, dataset):
        self.no_of_stations = no_of_stations
        self.no_of_vehicles = no_of_vehicles
        self.dataset = dataset
        self.Tmax = 3000
        df = pd.read_table(f'../dataset/new_dataset/{no_of_stations}/{no_of_stations}_tw_st_{dataset}.txt', sep=';', header=None)
        self.smin = list(df.loc[0:no_of_stations+1, 5])
        self.smax = list(df.loc[0:no_of_stations+1, 6])
        self.op = list(df.loc[0:no_of_stations+1, 3])
        self.cl = list(df.loc[0:no_of_stations+1, 4])
        self.time_matrix = pd.read_table(f'../dataset/new_dataset/{no_of_stations}/{no_of_stations}_timematrix_{dataset}.txt', sep=';',
                                    header=None).to_numpy()
        self.Rate = [1 for _ in range(no_of_stations+1)]
