#!/usr/bin/env python3

import io

from solution import *

P = """
# this is a comment
P 4
20 30 40
   50 60
      70
R 5
10 1 2 1
15 1 3 1
16 2 3 1
20 2 1 1
25 1 2 2
V 2
4
5
"""

S = [('Pickup', 0, 3, 30.0), ('Pickup', 1, 4, 25.0), ('Pickup', 1, 0, 25.0),
     ('Dropoff', 1, 4, 75.0), ('Dropoff', 1, 0, 75.0), ('Pickup', 0, 2, 30.0),
     ('Dropoff', 0, 3, 80.0), ('Pickup', 0, 1, 80.0), ('Dropoff', 0, 1, 140.0),
     ('Dropoff', 0, 2, 140.0)]

C = 144

def main():
    problem = FleetProblem()
    with io.StringIO(P) as fh:
        problem.load(fh)
    cost = problem.cost(S)
    print(f"Computed cost = {cost} ({'OK' if cost==C else 'NOK'})")

        
if __name__=='__main__':
    main()

# EOF
