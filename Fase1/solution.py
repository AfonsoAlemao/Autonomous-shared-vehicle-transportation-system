# import math

import search

class FleetProblem(search.Problem):    
    def __init__(self):
        self.req = [] # Store the requests
        self.t_opt = {} # Store the optimal transportation times
        self.vehicles = [] # Store the vehicles
        self.NP = 0 # Number of all pickup/drop-off points
        self.NR = 0 # Number of requests
        self.NV = 0 # Number of vehicles
        
    def load(self, fh):
        ''' Loads a problem from the opened file object fh. '''
        
        # Read file line by line and store in a list
        data = fh.readlines()
        
        # mode = 0 (not read data); 
        # mode = 1 (read transportation times); 
        # mode = 2 (read requests); 
        # mode = 3 (read vehicles)
        mode = 0 
        
        # max_capacity = 0 # maximum number of passengers in a vehicle
        # max_capacity_request = 0 # maximum number of passengers in a request
        counter = 0
        
        # Iterate through the input file lines
        for value in data:
            v = value.split()
           
            # Check if line is relevant 
            if v != [] and v[0] != "#":
                if v[0] == 'P': # Detect information about number of points     
                    # Check if line format meets specifications
                    # if len(v) < 2:
                    #     raise Exception("Invalid input file")
                    
                    NP = int(v[1])
                    # Valid problems have NP >= 1
                    # if NP < 1:
                    #     raise Exception("Invalid input file")
                    self.NP = NP
                    
                    mode = 1
                    counter = 0
                
                elif v[0] == 'R': # Detect information about number of requests
                    # Check if line format meets specifications
                    # if len(v) < 2:
                    #     raise Exception("Invalid input file")
                    
                    NR = int(v[1])
                    # Valid problems have NR >= 1
                    # if NR < 1:
                    #     raise Exception("Invalid input file")
                    self.NR = NR
                    
                    mode = 2
                    counter = 0
                    
                elif v[0] == 'V': # Detect information about number of vehicles
                    # Check if line format meets specifications
                    # if len(v) < 2:
                    #     raise Exception("Invalid input file")
                    
                    NV = int(v[1])
                    # Valid problems have NV >= 1
                    # if NV < 1:
                    #     raise Exception("Invalid input file")
                    self.NV = NV
                    
                    mode = 3
                    counter = 0
                    
                elif mode == 1: # Read transportation times
                    count_aux = counter + 1
                    for to in v:  
                        # Tod: Transportation time from origin (counter) to dropoff (count_aux)
                        Tod = float(to)
                        # Valid Tod >= 0
                        # if Tod < 0:
                        #     raise Exception("Invalid input file")
                        
                        origin = counter
                        drop_off = count_aux
                        self.t_opt[(origin, drop_off)] = Tod
                        count_aux += 1
                    counter += 1
                    
                elif mode == 2: # Read requests
                    # Check if line format meets specifications
                    # if len(v) < 4:
                    #     raise Exception("Invalid input file")
                    
                    req_time = float(v[0])
                    origin, drop_off = int(v[1]), int(v[2])
                    num_p = int(v[3])
                    
                    # Valid requests have request time >= 0, and number of passengers >= 1
                    # if origin == drop_off we consider Tod = 0
                    # if req_time < 0 or num_p < 1:
                    #     raise Exception("Invalid input file")

                    self.req.append((req_time, origin, drop_off, num_p)) # TODO
                    
                    # Update the maximum number of passengers in a request
                    # if num_p > max_capacity_request:
                    #     max_capacity_request = num_p
                        
                    counter += 1
                    
                elif mode == 3: # Read vehicles
                    # Check if line format meets specifications
                    # if len(v) < 1:
                    #     raise Exception("Invalid input file")
                    
                    capacity = int(v[0])
                    # Valid vehicles have number of passengers >= 1 
                    # if capacity < 1:
                    #         raise Exception("Invalid input file")
                    self.vehicles.append(capacity)
                    
                    # Update maximum number of passengers in a vehicle
                    # if capacity > max_capacity:
                    #     max_capacity = capacity
                    counter += 1
        
        # Check if the number of requests/vehicles matches the number of requests/vehicles in the request/vehicles list
        # The number of direct paths must be equal to NP C 2 (combinations of NP in pairs)
        # if math.comb(self.NP, 2) != len(self.t_opt) or self.NR != len(self.req) or self.NV != len(self.vehicles):
        #     raise Exception("Invalid input file") 
        
        # Check if we can fulfill all requests
        # if max_capacity_request > max_capacity:
        #     raise Exception("Invalid input file") 
        
        # Transportation time is 0 if origin == dropoff
        for p in range(NP):
            self.t_opt[(p, p)] = 0

                        
    def cost(self, sol):
        ''' Compute cost of solution sol. '''
        cost = 0         
    
        # structure of solution element, i.e, an action: (pic_drop, v_i, r_i, t)
        # pic_drop: a string, either ‘Pickup’ or  ́Dropoff’, with self-evident meaning;
        # v_i: an integer corresponding to the vehicle index;
        # r_i: an integer corresponding to the request index;
        # t: a float corresponding to the time of the action
        for action in sol:
            pic_drop, _, r_i, td = action
            
            if pic_drop == 'Dropoff':
                t_req, origin, drop_off, _  = self.req[r_i]
                
                # Get Tod of the request
                if origin > drop_off:
                    origin, drop_off = drop_off, origin
                Tod = self.t_opt[(origin, drop_off)]
                
                # Delay (dr) = 
                # = Dropoff time of an action (td) -
                # - Time of the request of an action (treq) -
                # - Optimal transportation time between origin and drop_off (Tod)
                dr = td - t_req - Tod
                
                # Cost of sol = sum of the request's delay
                cost += dr
                   
        return cost 
