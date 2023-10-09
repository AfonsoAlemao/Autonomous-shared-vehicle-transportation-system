import search

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
            
        print(self.req)

                        
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
        
        status_req = [False for _ in self.req] # False: Dropoff not done, True: Dropoff already done
        cost = 0  
        veh_status = [[] for _ in self.vehicles]

        # structure of solution element, i.e, an action: (pic_drop, v_i, r_i, t)
        # pic_drop: a string, either 'Pickup' or 'Dropoff', with self-evident meaning;
        # v_i: an integer corresponding to the vehicle index;
        # r_i: an integer corresponding to the request index;
        # t: a float corresponding to the time of the action
        for action in sol:
            pic_drop, v_i, r_i, td = action
            
            # Para cada veiculo, ver onde ele está (ponto do ultimo pickup/dropoff), descobrir o j
            if veh_status[v_i] != []:
                if td > veh_status[v_i][3]:
                    veh_status[v_i] = action
                # elif td == veh_status[v_i][3]:
                #     if veh_status[v_i][0] == 'Pickup' and pic_drop == 'Pickup':
                #         veh_status[v_i] = []
                #     else:
                #         veh_status[v_i] = action
            else:
                veh_status[v_i] = action
            
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
                
                status_req[r_i] = True
                
        for action in sol:
            pic_drop, v_i, r_i, tp = action
        
            if pic_drop == 'Pickup' and status_req[r_i] == False:
                t_req, origin, drop_off, _  = self.req[r_i]
                
                # Delay (dr) = 
                # = Pickup time of an action (td) -
                # - Time of the request of an action (treq)
                dr1 = tp - t_req 
                
                
                # atraves do veiculo associado ao pickup i, decobrir coisas sobre o j
                if veh_status[v_i] != []:
                    a_j, _, r_j, tp_j = veh_status[v_i]
                    origin_j, drop_off_j = self.req[r_j][1], self.req[r_j][2]
                    
                    if a_j == 'Pickup':
                        #td_i_real = tp_j+T(origin_j,destiny_i)
                        if origin_j < drop_off:
                            td_i_real = tp_j + self.t_opt[(origin_j, drop_off)]
                        else:
                            td_i_real = tp_j + self.t_opt[(drop_off, origin_j)]
                    else:
                        #td_i_real = tp_j+T(origin_j,destiny_i)
                        if drop_off_j < drop_off:
                            td_i_real = tp_j + self.t_opt[(drop_off_j, drop_off)]
                        else:
                            td_i_real = tp_j + self.t_opt[(drop_off, drop_off_j)]
                            
                    #td_iopt = tpi+T(origin_i,destiny_i)
                    if origin < drop_off:
                        td_iopt = tp + self.t_opt[(origin, drop_off)]
                    else:
                        td_iopt = tp + self.t_opt[(drop_off, origin)]

                    dr2 = td_i_real - td_iopt
                    
                else:
                    dr2 = 0
                        
                # Cost of sol = sum of the request's delay
                cost += dr1 + dr2
        # print(cost)
        return cost 
    
    def result(self, state, action):
        # print(action)
        if state == ''or state=='None':
            state = []
        else:
            state = list(eval(state))

        state.append(action)
        
        # print(state)
        
        # sort state
        state = sorted(state, key=lambda x: (x[3], x[0][0], x[1], x[2]))
        
        ''' Return the state that results from executing
        the given action in the given state '''
        
        # Pass list of tuples to string
        
        # Using a list comprehension to format the tuples as strings
        tuple_strings = [f'(\'{x}\', {y}, {z}, {w})' for x, y, z, w in state]

        # Joining the formatted tuples into a single string, separated by commas
        result_string = ', '.join(tuple_strings)
        return '[' + result_string + ']'
        
    
    def actions(self, state):
        ''' Return the actions that can be executed the given state . '''
        R = []
        available_seats = self.vehicles.copy()
        req_status = [[0,-1] for __ in range(self.NR)] # status of requirements status = 0 (start), status = 1 (picked up), status = 2 (finished)
        #status[1] is the vehicle in charge of the request
        
        if state == '' or state == 'None':
            state = []
        else:
            state = list(eval(state))
        
        for s in state:
            req_status[s[2]][0] +=1
            if s[0] == 'Pickup':
                req_status[s[2]][1] = s[1]
                available_seats[s[1]] -= self.req[s[2]][3]
            else:
                available_seats[s[1]] += self.req[s[2]][3]

        for index,request in enumerate(self.req):
            if(req_status[index][0] == 0):
                R.append(('Pickup', index))
            elif(req_status[index][0] == 1):
                R.append(('Dropoff', index))
        actions = []

        for request in R:
            for indexV,_ in enumerate(self.vehicles):

                if (request[0] == 'Dropoff' and indexV == req_status[request[1]][1]) or (request[0] == 'Pickup' and available_seats[indexV] >= self.req[request[1]][3]) :
                    #vehicle is appropriate for this specific task
                    
                    a = request[0]
                    v = indexV
                    r = request[1]
                    
                    # Iterar pelas state_actions e guardar última action relativa ao v_i (action_j).
                    # A partir deste ponto de partida para o veiculo calcular o tempo em que ele está disponivel para começar ação:
                    # Ponto da action = (origin if pickup/destiny if dropoff)
                    
                    action_j = []
                    for st_action in reversed(state):
                        if st_action[1] == v:
                            action_j.append(st_action)
                            break
                    
                    # Casos possíveis:
                    # .v_i nunca foi usado: 
                    # t = tempo que demora do ponto 0 até ao ponto da action
                    
                    if action_j == []:
                        # always 'Pickup':
                        new_action_point = self.req[request[1]][1] # get origin from request
                        
                        t = max(self.t_opt[(0, new_action_point)], self.req[request[1]][0]) 
                        # max(tempo de 0 até novo ponto; tempo do request no novo ponto)

                    else: 
                        # .v_i fez pickup/drop-off no ponto j: 
                        # t = t_drop/pick_j + tempo de ir de j para ponto da action 

                        if action_j[0][0] == 'Pickup':
                            action_j_point = self.req[action_j[0][2]][1] # get origin from request
                        else:
                            action_j_point = self.req[action_j[0][2]][2] # get destiny from request
                        
                        if a == 'Pickup':
                            new_action_point = self.req[request[1]][1] # get origin from request
                        else:
                            new_action_point = self.req[request[1]][2] # get destiny from request
                            
                        if action_j_point > new_action_point :
                            action_j_point,new_action_point = new_action_point, action_j_point
                            
                        t = max(action_j[0][3] + self.t_opt[(action_j_point, new_action_point)], self.req[request[1]][0])
                            
                    actions.append((a,v,r,t))
        # print(actions)
        return actions        
    
    def goal_test(self, state):
        ''' Return True if the state is a goal .''' 
        if state == '' or state == 'None':
            state = []
        else:
            state = list(eval(state))
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
