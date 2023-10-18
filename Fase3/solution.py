import search
import numpy 
from itertools import permutations

INFINITY = numpy.inf

''' Format a string to a list of tuples '''
def str_to_list_of_tuples(str):
    if str == '' or str == 'None':
        str = []
    else:
        str = list(eval(str))
    return str

''' Format a list of tuples [(a, b, c, d), ...] to string '''
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
        self.initial = ''  # Initial state is an empty string (empty list of tuples when we convert it)
    
    ''' Loads a problem from the opened file object fh. '''  
    def load(self, fh):  
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
                        
                        # T(p, q) > 0 if p ̸= q (as is in the project handout)
                        if Tod <= 0:
                            raise Exception("Invalid transportation time")
                
                        self.t_opt[(counter, count_aux)] = Tod # (origin, dropoff) = (counter, count_aux)
                        count_aux += 1
                    counter += 1
                    
                elif mode == 2: # Read requests
                    req_time = float(v[0])
                    
                    # Valid requests have t (request time) ≥ 0 (as is in the project handout)
                    if req_time < 0:
                        raise Exception("Invalid request time")

                    self.req.append((req_time, int(v[1]), int(v[2]), int(v[3]))) # (reqtime, origin, drop_off, num_p) 
                    counter += 1
                    
                elif mode == 3: # Read vehicles
                    self.vehicles.append((int(v[0]), counter)) # capacity
                    counter += 1 
        
        # Transportation time is 0 if origin == dropoff: T(p, p) = 0  (as is in the project handout)
        for p in range(self.NP):
            self.t_opt[(p, p)] = 0
        
        self.vehicles = sorted(self.vehicles, key=lambda x: (x[0]), reverse=True)
        if self.NR < self.NV:
            self.vehicles = self.vehicles[0 : self.NR]
            self.NV = self.NR
            
    ''' Compute cost of solution sol. '''       
    def cost(self, sol):
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
                Tod = self.Tod(origin, drop_off)
                
                # Delay (dr) = 
                # = Dropoff time of an action (td) -
                # - Time of the request of an action (t_req) -
                # - Optimal transportation time between origin and drop_off (Tod)
                dr = td - t_req - Tod
                
                # Cost of sol = sum of the request's delay
                cost += dr
                   
        return cost 
    
    ''' Compute cost of solution sol. It also considers incomplete solutions 
    by including delays of partially completed requests (only picked up). '''
    def cost2(self, sol):
        cost = 0
        # status_req = [False for _ in self.req] # (False): Dropoff not done yet; (True): Dropoff already done
        
        # veh_status = {} # Last action performed by the vehicle
        # valid_vehicle_index = [t[1] for t in self.vehicles]
        # for index in valid_vehicle_index:
        #     veh_status[(index)] = []

        # structure of solution element, i.e, an action: (pic_drop, v_i, r_i, t)
        # pic_drop: a string, either 'Pickup' or 'Dropoff', with self-evident meaning;
        # v_i: an integer corresponding to the vehicle index;
        # r_i: an integer corresponding to the request index;
        # t: a float corresponding to the time of the action
        for action in sol:
            pic_drop, _, r_i, td = action
            
            # For each vehicle, check its previous action
            # if veh_status[(v_i)] != []:
            #     if td > veh_status[(v_i)][3]:
            #         veh_status[(v_i)] = action
            # else:
            #     veh_status[(v_i)] = action
            
            # If a request has already been fulfilled, its cost is determined by the delay
            if pic_drop == 'Dropoff':
                t_req, origin, drop_off, _  = self.req[r_i]
                
                # Get Tod of the request
                Tod = self.Tod(origin, drop_off)
                
                # Request Cost = Delay = 
                # = Dropoff time of an action (td) -
                # - Time of the request of an action (t_req) -
                # - Optimal transportation time between origin and drop_off (Tod)                
                cost += td - t_req - Tod
                
                # status_req[r_i] = True
                
        # for action in sol:
        #     pic_drop, v_i, r_i, tp = action
        
        #     # In cases where request pickup has been done and dropoff hasn't,
        #     # we need to compute a estimated delay = dr1 + dr2 <= real (future) delay
        #     if pic_drop == 'Pickup' and status_req[r_i] == False:
        #         t_req, origin, drop_off, _  = self.req[r_i]
                
        #         # Delay (dr1) = 
        #         # = Pickup time of an action (td) -
        #         # - Time of the request of an action (t_req)
        #         dr1 = tp - t_req 
                
        #         # dr2 = td_i_estimated - td_iopt
        #         # where td_iopt: the optimal dropoff time for this request
        #         # td_i_estimated: the estimated dropoff time for this request, considering
        #         # the current location of the vehicle by its previous action, and that it is going 
        #         # from that point to the destination of the request (optimistic case)
        #         if veh_status[v_i] != []:
        #             a_j, _, r_j, tp_j = veh_status[v_i] # get the last action executed by the vehicle
        #             origin_j, drop_off_j = self.req[r_j][1], self.req[r_j][2]
                    
        #             if a_j == 'Pickup':
        #                 # td_i_estimated = tp_j + Tod(origin_j, destiny_i)
        #                 if origin_j < drop_off: # t_opt[(i, j)] must have i <= j
        #                     td_i_estimated = tp_j + self.t_opt[(origin_j, drop_off)]
        #                 else:
        #                     td_i_estimated = tp_j + self.t_opt[(drop_off, origin_j)]
        #             else:
        #                 # td_i_estimated = tp_j + Tod(origin_j, destiny_i)
        #                 if drop_off_j < drop_off:
        #                     td_i_estimated = tp_j + self.t_opt[(drop_off_j, drop_off)]
        #                 else:
        #                     td_i_estimated = tp_j + self.t_opt[(drop_off, drop_off_j)]
                            
        #             # td_iopt = tpi + Tod(origin_i, destiny_i)
        #             if origin < drop_off:
        #                 td_iopt = tp + self.t_opt[(origin, drop_off)]
        #             else:
        #                 td_iopt = tp + self.t_opt[(drop_off, origin)]

        #             dr2 = td_i_estimated - td_iopt             
        #         else:
        #             dr2 = 0
                        
        #         # Cost of sol = sum of the request's delay
        #         cost += dr1 + dr2

        return cost 
    
    ''' Return the state that results from executing
        the given action in the given state '''
    def result(self, state, action):
        # We use as state a string in order to use explored.add(node.state)
        # However state can only be manipulated in list of tuples format
        state = str_to_list_of_tuples(state)
        state.append(action)
    
        # Sort state in order to ensure the correct working of the priority queue (without duplicates)
        state = sorted(state, key=lambda x: (x[3], x[0][0], x[1], x[2]))
        return list_of_tuples_to_str(state)
        
    ''' Return the actions that can be executed in the given state. '''
    def actions(self, state):
        R = []
        
        available_seats = {}
        
        for seats, v_i in self.vehicles:
            available_seats[(v_i)] = seats

        req_status = [[0,-1] for __ in range(self.NR)]  # status of each request [0,1]
        # (0): status of requirements 0 (start), 1 (picked up), 2 (finished)
        # (1): index of the vehicle in charge of the request
        
        state = str_to_list_of_tuples(state)
        
        # Get the number of currently available seats in each vehicle, the 
        # status of each request and the index of the vehicle associated with each request
        for s in state:
            req_status[s[2]][0] +=1
            if s[0] == 'Pickup':
                req_status[s[2]][1] = s[1]
                available_seats[(s[1])] -= self.req[s[2]][3]
            else:
                available_seats[(s[1])] += self.req[s[2]][3]

        # R gets the feasible requests' actions available to be executed
        for index,request in enumerate(self.req):
            if(req_status[index][0] == 0):
                R.append(('Pickup', index))
            elif(req_status[index][0] == 1):
                R.append(('Dropoff', index))
                
        actions = []
        for request in R:
            for _, indexV in self.vehicles:
                # Check if vehicle is appropriate for this specific task:
                # in pickups check if the vehicle has available seats
                # in dropoffs check if this is the same vehicle that is performing that request
                if (request[0] == 'Dropoff' and indexV == req_status[request[1]][1]) or \
                    (request[0] == 'Pickup' and available_seats[(indexV)] >= self.req[request[1]][3]):
                    
                    # Save the vehicle's last action
                    action_j = []
                    for st_action in reversed(state):
                        if st_action[1] == indexV:
                            action_j.append(st_action)
                            break
                    
                    # Check if vehicle has ever been used
                    if action_j == []:
                        new_action_point = self.req[request[1]][1] # get origin from request, because always 'Pickup'
                        t = max(self.t_opt[(0, new_action_point)], self.req[request[1]][0]) 
                        # t = max(time from point 0 to new action's point, t_req)
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
                            
                        # t = max(t_drop/pick_j + time from point j to new action's point , t_req)
                        t = max(action_j[0][3] + self.Tod(action_j_point, new_action_point), self.req[request[1]][0])
                            
                    actions.append((request[0], indexV, request[1], t))
                    # action = (pickup/dropoff, vehicle index, request index, time)

        return actions        
    
    ''' Return True if the state is a goal. ''' 
    def goal_test(self, state):
        state = str_to_list_of_tuples(state)
        # Solution is complete if it has number of elements = 2 * number of requests,
        # i.e, a pickup and a dropoff per request
        return len(state) == len(self.req) * 2
    
    ''' Return the cost of a solution path that arrives at state2. '''
    def path_cost(self, c, state1, action, state2):
        return self.cost2(str_to_list_of_tuples(state2)) 
    
    def Tod(self, o, d):
        if o < d:
            return self.t_opt[(o, d)]
        else:
            return self.t_opt[(d, o)]
    
    def h(self, state):
        ''' Return the heuristic value for the given state.'''
        # given node n returns a cost estimate of the cheapest path from n to a goal node
        sol = str_to_list_of_tuples(state.state)
            
        cost = 0
        status_req = [0 for _ in self.req] 
        # (0,1): Dropoff not done yet; (2): Dropoff already done; 
        # (0): Pickup not done yet; (1,2): Pickup already done
        
        veh_status = {} # Last action performed by the vehicle
        veh_pic_status = {} # For each vehicle, save the request in course (pickup done, dropoff not done)
        valid_vehicle_index = [t[1] for t in self.vehicles]
        for index in valid_vehicle_index:
            veh_status[(index)] = []
            veh_pic_status[(index)] = []

        # structure of solution element, i.e, an action: (pic_drop, v_i, r_i, t)
        # pic_drop: a string, either 'Pickup' or 'Dropoff', with self-evident meaning;
        # v_i: an integer corresponding to the vehicle index;
        # r_i: an integer corresponding to the request index;
        # t: a float corresponding to the time of the action
        for action in sol:
            pic_drop, v_i, r_i, td = action
            
            # For each vehicle, check its previous action
            if veh_status[(v_i)] != []:
                if td > veh_status[(v_i)][3]:
                    veh_status[(v_i)] = action
            else:
                veh_status[(v_i)] = action
            
            # If a request has already been fulfilled, its cost is determined by the delay
            if pic_drop == 'Dropoff' or pic_drop == 'Pickup':
                status_req[r_i] += 1
                
        for action in sol:
            pic_drop, v_i, r_i, tp = action
        
            # In cases where request pickup has been done and dropoff hasn't,
            # we need to compute a estimated delay = dr1 + dr2 <= real (future) delay
            if pic_drop == 'Pickup' and status_req[r_i] != 2:
                veh_pic_status[(v_i)].append(action)
                t_req, origin, drop_off, _  = self.req[r_i]
                
                # Delay (dr1) = 
                # = Pickup time of an action (tp) -
                # - Time of the request of an action (t_req)
                dr1 = tp - t_req 
                
                # dr2 = td_i_estimated - td_iopt
                # where td_iopt: the optimal dropoff time for this request
                # td_i_estimated: the estimated dropoff time for this request, considering
                # the current location of the vehicle by its previous action, and that it is going 
                # from that point to the destination of the request (optimistic case)
                if veh_status[(v_i)] != []:
                    a_j, _, r_j, tp_j = veh_status[(v_i)] # get the last action executed by the vehicle
                    origin_j, drop_off_j = self.req[r_j][1], self.req[r_j][2]
                    
                    if a_j == 'Pickup':
                        # td_i_estimated = tp_j + Tod(origin_j, destiny_i)
                        td_i_estimated = tp_j + self.Tod(origin_j, drop_off)
                    else:
                        # td_i_estimated = tp_j + Tod(origin_j, destiny_i)
                        td_i_estimated = tp_j + self.Tod(drop_off_j, drop_off)
                            
                    # td_iopt = tpi + Tod(origin_i, destiny_i)
                    td_iopt = tp + self.Tod(drop_off, origin)

                    dr2 = td_i_estimated - td_iopt             
                else:
                    dr2 = 0
                        
                # Cost of sol = sum of the request's delay
                cost += dr1 + dr2
                
        # We also need to compute the estimated cost for the not attended requests
        for r_i, req in enumerate(self.req):
            if status_req[r_i] == 0:
                t_req, origin, drop_off, n_pass = req
                
                # Delay (dr1) = 
                # = Pickup time of an action (tp) -
                # - Time of the request of an action (t_req)
                # t_req = req[0]
            
                # tp = tp_i_estimated = the estimated pickup time for this request, considering
                # the current location of the vehicle by its previous action, and that it is going 
                # from that point to the pickup of the request (optimistic case)

                # try all vehicles and choose the one that guarantees optimality
                dr1_min = INFINITY
                
                # We do not consider the number of current passengers, to consider the 'best case'

                best_case = False
                for capacity, v_i in self.vehicles:
                    if capacity >= n_pass:
                        free_seats = capacity
                        for a in veh_pic_status[(v_i)]:
                            free_seats -= self.req[a[2]][3]
                            
                        if free_seats >= n_pass:
                            if veh_status[(v_i)] != []:
                                a_j, _, r_j, tp_j = veh_status[(v_i)] # get the last action executed by the vehicle
                                origin_j, drop_off_j = self.req[r_j][1], self.req[r_j][2]
                                
                                if a_j == 'Pickup':
                                    # tp_i_estimated = tp_j + Tod(origin_j, origin_i)
                                    tp = tp_j + self.Tod(origin_j, origin)
                                else:
                                    # td_i_estimated = tp_j + Tod(origin_j, origin_i)
                                    tp = tp_j + self.Tod(drop_off_j, origin)
                            else:
                                tp = self.t_opt[(0, origin)]
                            
                            if tp > t_req:   
                                dr1 = tp - t_req
                            else:
                                dr1 = 0
                                best_case = True
                        else:
                            a_j, _, r_j, tp_j = veh_status[(v_i)] # get the last action executed by the vehicle
                            origin_j, drop_off_j = self.req[r_j][1], self.req[r_j][2]
                            if a_j == 'Pickup':
                                point_j = origin_j
                            else:
                                point_j = drop_off_j
                                
                            # tp = tp_j + t_free 
                            
                            # tempo que ele demora a fazer dropoffs até ficar com espaço + t(ultimo dropoff, origin) = t_free                            
                            
                            # lista de pickups incompletos [p1(o1,d1,np1),p2(o2,d2,np2),p3(o3,d3,np3)] veh_pic_status[(v_i)]:
                            # list de possiveis dropoffs: 
                            permutations_list = list(permutations(veh_pic_status[(v_i)]))
                            
                            dr1_free_min = INFINITY
                            
                            # if len(permutations_list) > 1 and n_pass > 2:
                            #     print('a')
                            
                            for perm in permutations_list:
                                actual_point = point_j
                                t_free = 0
                                free_seats_aux = free_seats
                                delay_aux = 0
                                # list de possiveis dropoffs: 
                                for ii, act in enumerate(perm):
                                    req = self.req[act[2]]
                                    t_free += self.Tod(actual_point, req[2])
                                    if ii > 0:
                                        delay_aux += t_free - self.Tod(point_j, req[2])
                                            
                                    free_seats_aux += req[3]
                                    
                                    if free_seats_aux >= n_pass:
                                        t_free += self.Tod(req[2], origin)
                                        break
                                    
                                    actual_point = req[2]
                                    
                                    if tp_j + t_free - t_req + delay_aux >= dr1_min:
                                        break
                                
                                tp = tp_j + t_free
                                if tp > t_req:   
                                    dr1 = tp_j + t_free - t_req + delay_aux
                                else:
                                    dr1 = 0
                                    best_case = True
                                
                                if dr1 < dr1_free_min:
                                    dr1_free_min = dr1                                
                              
                            dr1 = dr1_free_min
                        
                        if dr1 < dr1_min:
                            dr1_min = dr1
                        
                
                    if best_case == True:
                        break
                
                cost += dr1_min

        return cost 
        
    ''' Calls the informed search algorithm
        chosen. Returns a solution using the specified format. '''
    def solve(self):
        # We chose the uniform cost search algorithm which selects the node 
        # with lower path cost by using a priority queue.
        # Advantages: guarantees optimal solution and completeness 
        # given that step costs are strictly positive.
        # Time and space complexity: proportional to number of nodes with path cost
        # less than of optimal solution.

        # Assignment 2: Uninformed search
        # solution = search.uniform_cost_search(self)
        solution = search.astar_search(self, h=self.h, display=True)
        return str_to_list_of_tuples(solution.state)
