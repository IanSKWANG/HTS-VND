newList="500 1000"
truckList="1 2 3 10"
dataset="1 2 3"
for i in $newList; do for j in $truckList; do for k in $dataset; do
    python cp.py --size $i --ntruck $j --dataset $k
done; done; done