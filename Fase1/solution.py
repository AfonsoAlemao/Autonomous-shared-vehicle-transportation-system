import math

import search

class FleetProblem(search.Problem):
    
    def __init__(self):
        self.req = []
        self.t_opt = {}
        self.vehicles = []
        self.NP = 0
        self.NR = 0
        self.NV = 0
        
    def load(self, fh) :
        ''' Loads a problem from the opened file object fh. '''
        #Read file line by line and store in a list
        data = fh.readlines()
        
        mode = 0 # mode = 0 (not read data); mode = 1 (read transportation times); mode = 2 (read requests); mode = 3 (read vehicles)
        
        max_capacity = 0
        max_capacity_request = 0
        
        counter = 0
        
        #Iterate the list and print each value
        for value in data:
            
            v = value.split()
           
            if v != [] and v[0] != "#": 
                
                v = value.split()
           
                
                if v[0] == 'P':
                    if len(v) < 2:
                        raise Exception("Invalid input file")
                    
                    NP = int(v[1])
                    if NP < 1:
                        raise Exception("Invalid input file")
                    self.NP = NP
                    mode = 1
                    counter = 0
                    
                elif v[0] == 'R':
                    if len(v) < 2:
                        raise Exception("Invalid input file")
                    
                    NR = int(v[1])
                    if NR < 1:
                        raise Exception("Invalid input file")
                    self.NR = NR
                    mode = 2
                    counter = 0
                    
                elif v[0] == 'V':
                    if len(v) < 2:
                        raise Exception("Invalid input file")
                    
                    NV = int(v[1])
                    if NV < 1:
                        raise Exception("Invalid input file")
                    self.NV = NV
                    mode = 3
                    counter = 0
                    
                elif mode == 1:
                    count_aux = counter + 1
                    for to in v:  
                        Tod = float(to)
                        
                        if Tod < 0:
                            raise Exception("Invalid input file")
                        
                        origin = counter
                        drop_off = count_aux
                        self.t_opt[(origin, drop_off)] = Tod
                        count_aux += 1
                    counter += 1
                    
                elif mode == 2:
                    if len(v) < 4:
                        raise Exception("Invalid input file")
                    
                    req_time = float(v[0])
                    origin, drop_off = int(v[1]), int(v[2])
                    num_p = int(v[3])
                    
                    if origin == drop_off or req_time < 0 or num_p < 1:
                        raise Exception("Invalid input file")

                    self.req.append(tuple([req_time, origin, drop_off, num_p]))
                    
                    if num_p > max_capacity_request:
                        max_capacity_request = num_p
                        
                    counter += 1
                    
                elif mode == 3:
                    capacity = int(v[0])
                    if capacity < 1:
                            raise Exception("Invalid input file")
                    self.vehicles.append(capacity)
                    if capacity > max_capacity:
                        max_capacity = capacity
                    counter += 1
        
        # Check if the number of requests/vehicles matches the number of requests/vehicles in the request/vehicles list
        # The number of direct paths must be equal to NP C 2 (combinations of NP in pairs)
        if math.comb(self.NP, 2) != len(self.t_opt) or self.NR != len(self.req) or self.NV != len(self.vehicles):
            raise Exception("Invalid input file") 
        
        # Check if we can fulfill all requests
        if max_capacity_request > max_capacity:
            raise Exception("Invalid input file") 
            
                        
    def isSolution(self, sol) :
        ''' Compute cost of solution sol. '''
        cost = 0
        print(sol)
        for action in sol:
            
            # type: a string, either ‘Pickup’ or  ́Dropoff’, with self-evident meaning;
            # v_i: an integer corresponding to the vehicle index;
            # r_i: an integer corresponding to the request index;
            # t: a float corresponding to the time of the action
            type, _, r_i, td = action
            if type == 'Dropoff':
                t_req, origin, drop_off, _  = self.req[r_i]
                
                if origin > drop_off:
                    origin, drop_off = drop_off, origin
                    
                Tod = self.t_opt[(origin, drop_off)]
                   
                dr = td - t_req - Tod
                cost += dr
                   
        return cost
