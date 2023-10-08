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

                    self.req.append((req_time, int(v[1]), int(v[2]), int(v[3]), 0)) # (reqtime, origin, drop_off, num_p, status) status = 0 (start), status = 1 (picked up), status = 2 (finished)
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
    
    def result(self, state, action):
        ''' Return the state that results from executing
        the given action in the given state '''
        return state.append(action)
        
    
    def actions(self, state):
        ''' Return the actions that can be executed the given state . '''
        R = []

        for index,request in enumerate(self.req):
            if(request[4] == 0):
                R.append(('Pickup', index))
            elif(request[4] == 1):
                R.append(('Dropoff', index))
        actions = []

        for indexR,request in enumerate(R):
            for indexV,capacity in enumerate(self.vehicles):
                #vehicle is appropriate for this specific task
                if capacity >= self.req[request[1]]:
                    a = request[0]
                    v = indexV
                    r = indexR
                    
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
                        
                        t = max(self.t_opt((0, new_action_point)), self.req[request[1]][0]) 
                        # max(tempo de 0 até novo ponto; tempo do request no novo ponto)

                    else: 
                        # .v_i fez pickup/drop-off no ponto j: 
                        # t = t_drop/pick_j + tempo de ir de j para ponto da action 

                        if a == 'Pickup':
                            action_j_point = self.req[action_j[2]][1] # get origin from request
                        else:
                            action_j_point = self.req[action_j[2]][2] # get destiny from request
                        
                        if a == 'Pickup':
                            new_action_point = self.req[request[1]][1] # get origin from request
                        else:
                            new_action_point = self.req[request[1]][2] # get destiny from request
                        
                        t = max(action_j[3] + self.t_opt((action_j_point, new_action_point)), self.req[request[1]][0])
                            
                    actions.append((a,v,r,t))
        
        return actions        
        # return super().actions(state)
    
    def goal_test(self, state):
        ''' Return True if the state is a goal .''' 
        return len(state) == len(self.req)*2
        # return super().goal_test(state)
    
    def path_cost(self, c, state1, action, state2):
        ''' Return the cost of a solution path that arrives at state 2 from
    state1 via action , assuming cost c to get up to state1 . '''

        state2 = self.result(state=state1, action=action)

        return self.cost(state2) 
    
    def solve(self):
        ''' Calls the uninformed search algorithm
        chosen . Returns a solution using the specified format . '''

        return search.uniform_cost_search(self)
