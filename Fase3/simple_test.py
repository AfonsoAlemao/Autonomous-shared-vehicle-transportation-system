import io
import sys
import json

from solution import *

test = sys.argv

File2  = open("../Test2/"+test[1]+".dat", "r")

P = File2.read()
File2.close()

# P = """
# # this is a comment
# P 4
# 20 30 40
#    50 60
#       70
# R 5
# 10 1 2 1
# 15 1 3 1
# 16 2 3 1
# 20 2 1 1
# 25 1 2 2
# V 2
# 4
# 5
# """

# S = [('Pickup', 0, 3, 30.0), ('Pickup', 1, 4, 25.0), ('Pickup', 1, 0, 25.0),
#      ('Dropoff', 1, 4, 75.0), ('Dropoff', 1, 0, 75.0), ('Pickup', 0, 2, 30.0),
#      ('Dropoff', 0, 3, 80.0), ('Pickup', 0, 1, 80.0), ('Dropoff', 0, 1, 140.0),
#      ('Dropoff', 0, 2, 140.0)]

# C = 144

# import time

def main():
    problem = FleetProblem()
    with io.StringIO(P) as fh:
        problem.load(fh)
        
    # start_time = time.time()
    solution = problem.solve()
    # print("--- %s seconds ---" % (time.time() - start_time))
    
    # print(solution)
    print(problem.cost(solution))

        
if __name__=='__main__':
    main()

# EOF

# Timings

# exi | t(inclui NEW) | t(NEW comentado)

# ex0|0.00s|0.00s
# ex1|0.00s|0.01s
# ex2|0.16s|0.46s
# ex3|2.36s|12.4s
# ex4|0.01s|15.9s
# ex5|16.2s|0.11s
# ex6|0.00s|0.00s
# ex7|0.02s|0.36s
# ex8|0.09s|0.57s
# ex9|0.07s|0.41s
 