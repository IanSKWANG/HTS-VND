import pandas as pd

def get_data(size, dataset):
    df = pd.read_table(f'../dataset/new_dataset/{size}/{size}_tw_st_{dataset}.txt', sep=';', header=None)
    n = int(size)
    smin = list(df.loc[0:n+1, 5])
    smax = list(df.loc[0:n+1, 6])
    op = list(df.loc[0:n+1,3])
    cl = list(df.loc[0:n+1,4])
    time_matrix = pd.read_table(f'../dataset/new_dataset/{size}/{size}_timematrix_{dataset}.txt', sep=';', header=None).to_numpy()
    return n, smin, smax, op, cl, time_matrix