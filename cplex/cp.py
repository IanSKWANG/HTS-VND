import datetime
from get_data import get_data
import pandas as pd
import numpy as np
import os
from docplex.mp.model import Model

from arg_parser import args
size = args.size
ntruck = args.ntruck
dataset = args.dataset
import importlib



n, smin, smax, op, cl, time_matrix = get_data(size, dataset)
print("get data done!")
Tmax = 3000
k = int(ntruck)  #numeber of uav
N = [i for i in range(1, n+1)] #station list
K = [i for i in range(1, k+1)] #UAV list
L = [0]+N
r = 1 #collection rate
M = 100000

A = [(i, j) for i in L for j in L if i != j]
t={(i,j):0 for i,j in A}
for i,j in A:
    t[(i,j)] = time_matrix[i,j]

UAV = [(i,j,k) for i,j in A for k in K]
arrival_time = [(i) for i in L]
service_time = [(i) for i in L]

mdl = Model("UAV_TWST")

#decision variables
x = mdl.binary_var_dict(UAV, name='x')
a = mdl.continuous_var_dict(arrival_time, name='a')
s = mdl.integer_var_dict(service_time, name='s')
l = mdl.continuous_var_dict(UAV, name='l')
#objective
mdl.maximize(mdl.sum(l[i,j,k]*r for i,j,k in UAV))

#constraints
mdl.add_constraints(mdl.sum(x[0,j,k] for j in N)==1 for k in K)
mdl.add_constraints(mdl.sum(x[i,0,k] for i in N)==1 for k in K)

mdl.add_constraints(mdl.sum(x[i,j,k] for i in L if i!=j for k in K) <= 1 for j in N)

mdl.add_constraints(mdl.sum(x[i,h,k] for i in L if i!=h) == mdl.sum(x[h,j,k] for j in L if j!=h) for h in N for k in K )


mdl.add_constraints(a[i] + l[i,j,k]+t[i,j]-a[j] <= M*(1-x[i,j,k]) for k in K for i in N for j in N if i!=j)

mdl.add_constraints(a[i] >= op[i] * mdl.sum(x[i,j,k] for j in L if j != i for k in K) for i in L)
mdl.add_constraints(a[i] <= cl[i] * mdl.sum(x[i,j,k] for j in L if j != i for k in K) for i in L)
mdl.add_constraints(a[i] <= Tmax - l[i,0,k] - t[i,0] for k in K for i in L if i!=0)
# mdl.add_constraint(a[0] <= Tmax)

mdl.add_constraints(smin[i] <= s[i] for i in L)
mdl.add_constraints(s[i] <= smax[i] for i in L)
# mdl.add_constraints(s[i]<= 500 for i in L)

mdl.add_constraints(s[i]<=cl[i]-a[i]+smin[i] for i in N)

# mdl.add_constraints(mdl.sum(x[i,j,k] * t[i,j] + l[i,j,k] for i in L for j in L if i!=j) <= Tmax for k in K)

mdl.add_constraint(a[0]==0)
mdl.add_constraint(s[0]==0)


mdl.add_constraints(l[i,j,k] - s[i] <= 0 for i in L for j in L if i!=j for k in K)
mdl.add_constraints(l[i,j,k]<= M * x[i,j,k] for i in L for j in L if i!=j for k in K)
mdl.add_constraints(s[i]-l[i,j,k]+M*x[i,j,k]<=M for i in L for j in L if i!=j for k in K)


mdl.set_time_limit(3600)
mdl.parameters.read.datacheck =2
mdl.parameters.emphasis.mip = 3
solution = mdl.solve(log_output = True)

if not os.path.exists(f'result/{size}_{dataset}'):
    os.makedirs(f'result/{size}_{dataset}')
res_file = open(f"result/{size}_{dataset}/cp_{size}_{dataset}_{k}.txt", 'w')
res_file.write(f"number of station = \t {n}\n")
res_file.write(f"number of UAV = \t {k}\n")
res_file.write(f"objective = \t {solution.objective_value}\n")
res_file.write(f"solve time = \t {mdl.solve_details.time}\n")
res_file.write(f"gap = \t {mdl.solve_details.gap}\n")
for i in L:
    for j in L:
        for k in K:
            if i != j and x[(i, j, k)].solution_value != 0:
                res_file.write(f"x[{i},{j},{k}]={x[(i, j, k)].solution_value}\n")

for i in L:
    # if a[(i)].solution_value != 0:
    res_file.write(f"a[{i}]={a[(i)].solution_value}\n")

for i in L:
    for j in L:
        for k in K:
            if i != j and l[(i, j, k)].solution_value != 0:
                res_file.write(f"d[{i},{j},{k}]={l[(i, j, k)].solution_value}\n")

