import time


'''
def Creat_FIB(self, route_ID):

def Get_fib(self, route_ID):

def Get_fib_entry(self, fib, content_name):

def Add_fib_outface(self, data, route_ID, fib_entry):

# Remove the content name with the most cost
def Remove_fib_entry(self,fib):

def Add_fib_entry(self, fib, data, route_ID):

# The outface is updated to fib
def Update_fib_outface_data(self, fib, route_ID, fib_size, data):

# Forward interest packets to all neighbors
def Broadcast(self, route_ID, inface):

# Choose the outface with the min cost to forward the interest packet
def Best_route(self, route_ID, inface, fib_entry):

# Find in FIB whether there is a matching interest packet entry
def Search_fib_interest(self, fib, route_ID, interest):
'''


class Network:
    def __init__(self):
        """
        self.network = {'r0': [1,3],'r1': [0,2,3],'r2': [1,5],'r3': [0,1,4],'r4': [3,5,6],'r5': [2,4,7],'r6': [4,7,10],
        'r7': [5,6,8,9],'r8': [7],'r9': [7,11],'r10': [6,11],'r11': [9,10]}
        """
        self.network = {}

    def network(self, network):
        self.network = network
        return self.network

    def get_network(self, network):
        self.network = network
        return self.network


class FIB:
    def __init__(self):
        self.fib = {}  # {'content_name': [[outface, cost, time], ...]}
        self.fib_entry = []

    def fib(self, route_id):
        return self.fib

    def get_fib(self, route_id):
        return self.fib

    @staticmethod
    def get_fib_entry(fib, content_name):
        """
        fib = {'content_name': [[outface, cost, time], ...], ... }
        fib_entry = [[outfibface, cost, time], ...]
        """
        if content_name in fib:
            fib_entry = fib[content_name]
            return fib_entry
        else:
            return []

    @staticmethod
    def add_fib_outface(data, route_id, fib_entry):
        """
        data = {'type': 'data', 'consumer_ID': 0, 'route_ID': 0, 'content_name': 'r0/0', 'content_data': '',
                'data_hop': 0, 'run_start_time': 0.0, 'path': ''}
        fib = {'content_name': [[outface, cost, time], ...], ... }
        fib_entry = [[outface, cost, time], ...]
        """
        outface = data['route_ID']
        # cost = abs(entry[1] - i)    # data['data_hop']
        # Record the time when outface was added
        times = int(time.process_time())  # time.clock()
        cost = data['data_hop']
        for entry in fib_entry:
            if entry[0] == outface:
                if cost < entry[1]:
                    entry[1] = cost
                    entry[2] = times
                    # Sort by cost from smallest to largest
                    fib_entry.sort(key=lambda i: (i[1]), reverse=False)
                return
        if len(fib_entry) < 1000:
            fib_entry.append([outface, cost, times])
        else:
            # remove the most costly outface
            fib_entry.pop(-1)  # x = fib_entry.pop(-1)
            fib_entry.append([outface, cost, times])
        # Sort by cost from smallest to largest
        fib_entry.sort(key=lambda i: (i[1]), reverse=False)
        return fib_entry

    @staticmethod
    def remove_fib_entry(fib):
        """
        fib = {'content_name': [[outface, cost, time], ...], ... }
        """
        # Find the content name with the most cost
        for key, value in fib.items():
            # if len(value) > 0:
            #     cost = value[0][1]
            # time = value[0][2]
            #     if cost > max:
            #         max = cost
            #         content_name =
            # if max != 0:content_name
            del fib[key]
            break

    @staticmethod
    def add_fib_entry(fib, data, route_id):
        """
        data = {'type': 'data', 'consumer_ID': 0, 'route_ID': 0, 'content_name': 'r0/0', 'content_data': '',
                'data_hop': 0, 'run_start_time': 0.0, 'path': ''}
        fib = {'content_name': [[outface, cost, time], ...], ... }
        fib_entry = [[outface, cost, time], ...]
        """
        content_name = data['content_name']
        outface = data['route_ID']
        times = int(time.process_time())  # time.clock()
        cost = data['data_hop']
        temp = {content_name: [[outface, cost, times]]}
        fib.update(temp)

    def update_fib_outface_data(self, fib, route_id, fib_size, data):
        """
        fib = {'content_name': [[outface, cost, time], ...], ... }
        fib_entry = [[outface, cost, time], ...]
        """
        content_name = data['content_name']
        fib_entry = self.get_fib_entry(fib, content_name)
        if len(fib_entry) == 0:
            if len(fib) > fib_size:
                self.remove_fib_entry(fib)
            self.add_fib_entry(fib, data, route_id)
        else:
            self.add_fib_outface(data, route_id, fib_entry)

    # Forward interest packets to all neighbors
    @staticmethod
    def forward(route_id, network, inface):
        outfaces = []
        net = Network()
        network = net.get_network(network)
        entry = network['r' + str(route_id)]
        for outface in entry:
            if outface != inface and outface != route_id:  #
                outfaces.append([outface, 1])  # outfaces=[[outface,cost],...]
        return outfaces

    # Choose outface with the min cost to forward the interest packet
    def best_route(self, route_id, network, inface, fib_entry):
        outface = []
        for entry in fib_entry:
            outface = entry[0]
            if outface != inface and outface != route_id:  #
                cost = entry[1]
                outface.append([outface, cost])  # outfaces=[[outface,cost],...]
                return outface
        if len(outface) == 0:
            outface = self.forward(route_id, network, inface)
        return outface

    # Find in FIB whether there is a matching interest packet entry
    def find_fib_interest(self, fib, route_id, network, interest):
        """
        interest = {'type': 'interest', 'interest_ID': 0, 'consumer_ID': 0, 'route_ID': 0, 'content_name': 'r0/0',
                    'interest_hop': 0, 'life_hop': 5, 'run_start_time': 0.0, 'path': ''}
        fib = {'content_name': [[outface, cost, time], ...], ... }
        """
        content_name = interest['content_name']
        inface = interest['route_ID']
        fib_entry = self.get_fib_entry(fib, content_name)
        if len(fib_entry) == 0:
            outfaces = self.forward(route_id, network, inface)
        else:
            # print(str(fib_entry) + ' ')
            outfaces = self.best_route(route_id, network, inface, fib_entry)
        # print(str(inface) + '-' + str(route_ID) + '= ' + str(outfaces))
        # print(str(outfaces) + '-' + str(Outfaces_temp)+' ')
        # print(str(Outfaces_temp) + ' ')
        return outfaces
