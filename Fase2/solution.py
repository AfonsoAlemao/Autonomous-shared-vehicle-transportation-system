import search
            
def str_to_list_of_tuples(str):
    if str == '' or str == 'None':
        str = []
    else:
        str = list(eval(str))
    
    return str

def list_of_tuples_to_str(state):
    # Using a list comprehension to format the tuples as strings
    tuple_strings = [f'(\'{x}\', {y}, {z}, {w})' for x, y, z, w in state]

    # Joining the formatted tuples into a single string, separated by commas
    result_string = ', '.join(tuple_strings)
    return '[' + result_string + ']'
    
class FleetProblem(search.Problem):    
    def __init__(self):
        self.req = [] # Store the requests
        self.t_opt = {} # Store the optimal transportation times
        self.vehicles = [] # Store the vehicles
        self.NP = 0 # Number of all pickup/drop-off points
        self.NR = 0 # Number of requests
        self.NV = 0 # Number of vehicles
        self.state = [] # state
        self.initial = ''
        
    def load(self, fh):
        ''' Loads a problem from the opened file object fh. '''
        counter = 0
        
        # Read file line by line and store in a list
        data = fh.readlines()
        
        # mode = 0 (do not read data), mode = 1 (read transportation times); 
        # mode = 2 (read requests), mode = 3 (read vehicles)
        mode = 0 
        
        # Iterate through the input file lines
        for value in data:
            v = value.split()
           
            # Check if line is relevant 
            if v != [] and v[0] != "#":
                if v[0] == 'P': # Detect information about number of points 
                    self.NP = int(v[1])
                    mode = 1
                    counter = 0
                
                elif v[0] == 'R': # Detect information about number of requests
                    self.NR = int(v[1])             
                    mode = 2
                    counter = 0
                    
                elif v[0] == 'V': # Detect information about number of vehicles
                    self.NV = int(v[1])
                    mode = 3
                    counter = 0
                    
                elif mode == 1: # Read transportation times
                    count_aux = counter + 1
                    for to in v:  
                        # Tod: Transportation time from origin (counter) to dropoff (count_aux)
                        Tod = float(to)
                        
                        # T(p, q) > 0 if p ̸= q (como está no enunciado)
                        if Tod <= 0:
                            raise Exception("Invalid transportation time")
                
                        self.t_opt[(counter, count_aux)] = Tod # (origin, dropoff) = (counter, count_aux)
                        count_aux += 1
                    counter += 1
                    
                elif mode == 2: # Read requests
                    req_time = float(v[0])
                    
                    # Valid requests have t (request time) ≥ 0 (como está no enunciado)
                    if req_time < 0:
                        raise Exception("Invalid request time")

                    self.req.append((req_time, int(v[1]), int(v[2]), int(v[3]))) # (reqtime, origin, drop_off, num_p) 
                    counter += 1
                    
                elif mode == 3: # Read vehicles
                    self.vehicles.append(int(v[0])) # capacity
                    counter += 1 
        
        # Transportation time is 0 if origin == dropoff: T(p, p) = 0  (como está no enunciado)
        for p in range(self.NP):
            self.t_opt[(p, p)] = 0
            
                        
    def cost(self, sol):
        ''' Compute cost of solution sol. '''
        cost = 0  

        # structure of solution element, i.e, an action: (pic_drop, v_i, r_i, t)
        # pic_drop: a string, either 'Pickup' or 'Dropoff', with self-evident meaning;
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
    
    def cost2(self, sol):
        ''' Compute cost of solution sol.
        It also considers imcomplete solutions including pickups withount dropoff '''
        
        cost = 0
        status_req = [False for _ in self.req] # False: Dropoff not done yet, True: Dropoff already done
        veh_status = [[] for _ in self.vehicles] # Last action performed by the vehicle

        # structure of solution element, i.e, an action: (pic_drop, v_i, r_i, t)
        # pic_drop: a string, either 'Pickup' or 'Dropoff', with self-evident meaning;
        # v_i: an integer corresponding to the vehicle index;
        # r_i: an integer corresponding to the request index;
        # t: a float corresponding to the time of the action
        for action in sol:
            pic_drop, v_i, r_i, td = action
            
            # For each vehicle, check where it is (point of the last pickup/dropoff)
            if veh_status[v_i] != []:
                if td > veh_status[v_i][3]:
                    veh_status[v_i] = action
            else:
                veh_status[v_i] = action
            
            # In case a request has already been fulfilled, its cost is equal to the delay
            if pic_drop == 'Dropoff':
                t_req, origin, drop_off, _  = self.req[r_i]
                
                # Get Tod of the request
                if origin > drop_off:
                    origin, drop_off = drop_off, origin
                Tod = self.t_opt[(origin, drop_off)]
                
                # ReqCost = Delay = 
                # = Dropoff time of an action (td) -
                # - Time of the request of an action (treq) -
                # - Optimal transportation time between origin and drop_off (Tod)                
                cost += td - t_req - Tod
                
                status_req[r_i] = True
                
        for action in sol:
            pic_drop, v_i, r_i, tp = action
        
            # In case where request pickup has been done and dropoff hasn't,
            # we need to compute a estimated delay = dr1 + dr2 <= real (future) delay
            if pic_drop == 'Pickup' and status_req[r_i] == False:
                t_req, origin, drop_off, _  = self.req[r_i]
                
                # Delay (dr1) = 
                # = Pickup time of an action (td) -
                # - Time of the request of an action (treq)
                dr1 = tp - t_req 
                
                # dr2 = td_i_estimated - td_iopt
                # where td_iopt: the optimal dropoff time for this request
                # td_i_estimated: the estimated dropoff time for this request, considering
                # the current location of the vehicle in its previous action, and that it is going 
                # from that point to the destination of the request (optimistic case)
                if veh_status[v_i] != []:
                    a_j, _, r_j, tp_j = veh_status[v_i] # get the last action executed by the vehicle
                    origin_j, drop_off_j = self.req[r_j][1], self.req[r_j][2]
                    
                    if a_j == 'Pickup':
                        # td_i_estimated = tp_j + Tod(origin_j, destiny_i)
                        if origin_j < drop_off:
                            td_i_estimated = tp_j + self.t_opt[(origin_j, drop_off)]
                        else:
                            td_i_estimated = tp_j + self.t_opt[(drop_off, origin_j)]
                    else:
                        # td_i_estimated = tp_j + Tod(origin_j, destiny_i)
                        if drop_off_j < drop_off:
                            td_i_estimated = tp_j + self.t_opt[(drop_off_j, drop_off)]
                        else:
                            td_i_estimated = tp_j + self.t_opt[(drop_off, drop_off_j)]
                            
                    # td_iopt = tpi + Tod(origin_i, destiny_i)
                    if origin < drop_off:
                        td_iopt = tp + self.t_opt[(origin, drop_off)]
                    else:
                        td_iopt = tp + self.t_opt[(drop_off, origin)]

                    dr2 = td_i_estimated - td_iopt             
                else:
                    dr2 = 0
                        
                # Cost of sol = sum of the request's delay
                cost += dr1 + dr2

        return cost 
    
    
    def result(self, state, action):
        ''' Return the state that results from executing
        the given action in the given state '''
        state = str_to_list_of_tuples(state)
        state.append(action)
                
        # Sort state in order to use the priority queue without duplicates
        state = sorted(state, key=lambda x: (x[3], x[0][0], x[1], x[2]))
        return list_of_tuples_to_str(state)
        
    
    def actions(self, state):
        ''' Return the actions that can be executed the given state . '''
        R = []
        available_seats = self.vehicles.copy() # number of available seats in each vehicle
        req_status = [[0,-1] for __ in range(self.NR)]  # status of each request (0,1)
        # (0): status of requirements 0 (start), 1 (picked up), 2 (finished)
        # (1): index of the vehicle in charge of the request
        
        state = str_to_list_of_tuples(state)
        
        # Get the number of current available seats in each vehicle
        # and get the status of each request
        for s in state:
            req_status[s[2]][0] +=1
            if s[0] == 'Pickup':
                req_status[s[2]][1] = s[1]
                available_seats[s[1]] -= self.req[s[2]][3]
            else:
                available_seats[s[1]] += self.req[s[2]][3]

        # R gets the feasible requests actions available to be executed
        for index,request in enumerate(self.req):
            if(req_status[index][0] == 0):
                R.append(('Pickup', index))
            elif(req_status[index][0] == 1):
                R.append(('Dropoff', index))
        actions = []

        for request in R:
            for indexV,_ in enumerate(self.vehicles):
                # Vehicle is appropriate for this specific task, i.e.,
                # in cases of pickup check if the vehicle has available seats and
                # in cases of dropoff check if it's the same vehicle that is performing that request
                if (request[0] == 'Dropoff' and indexV == req_status[request[1]][1]) or \
                    (request[0] == 'Pickup' and available_seats[indexV] >= self.req[request[1]][3]):
                    
                    # Save the last action by vehicle
                    action_j = []
                    for st_action in reversed(state):
                        if st_action[1] == indexV:
                            action_j.append(st_action)
                            break
                    
                    # Vehicle never used before
                    if action_j == []:
                        new_action_point = self.req[request[1]][1] # get origin from request, because always 'Pickup'
                        t = max(self.t_opt[(0, new_action_point)], self.req[request[1]][0]) 
                    else: 
                        if action_j[0][0] == 'Pickup':
                            action_j_point = self.req[action_j[0][2]][1] # get origin from request
                        else:
                            action_j_point = self.req[action_j[0][2]][2] # get destiny from request
                        
                        if request[0] == 'Pickup':
                            new_action_point = self.req[request[1]][1] # get origin from request
                        else:
                            new_action_point = self.req[request[1]][2] # get destiny from request
                            
                        if action_j_point > new_action_point :
                            action_j_point,new_action_point = new_action_point, action_j_point
                            
                        # t = t_drop/pick_j + time from point j to new action's point 
                        t = max(action_j[0][3] + self.t_opt[(action_j_point, new_action_point)], self.req[request[1]][0])
                            
                    actions.append((request[0], indexV, request[1], t))
                    # action = (pickoff/dropoff, vehicle index, request index, time)

        return actions        
    
    def goal_test(self, state):
        ''' Return True if the state is a goal .''' 
        state = str_to_list_of_tuples(state)
        
        return len(state) == len(self.req) * 2
    
    def path_cost(self, c, state1, action, state2):
        ''' Return the cost of a solution path that arrives at state 2 from
    state1 via action , assuming cost c to get up to state1 . '''
        return self.cost2(list(eval(state2))) 
    
    def solve(self):
        ''' Calls the uninformed search algorithm
        chosen . Returns a solution using the specified format . '''

        solution = search.uniform_cost_search(self)
        solution = list(eval(solution.state))
        return solution
