import ast

class FIB:
    def __init__(self):
        self.__fib = {}  # {'content_name': [[outface, cost, time], ...]}
        # self.__fib_entry = []
        # self.__fib_status_now = True
        # self.__fib_status_pre = True

    def get_fib(self):
        return self.__fib

    def select_nexthop(self, targetname):
        if targetname in self.__fib:
            item = self.__fib[targetname]
            return [item[0]]
        else: return [-1]

    def update_fib(self, pre_name, targetname):
        if pre_name in self.__fib[targetname]:
            self.__fib[targetname] += [targetname]

    def add_nexthop_fib(self, next_hop_name):
        self.__fib[next_hop_name] = []
        self.__fib[next_hop_name].append(next_hop_name)

    def delete_nexthop_fib(self, next_hop_name):
        for k, v in self.__fib.items():
            for next in v:
                if(next_hop_name == next):
                    v.remove(next)

    def broadcast_list(self):
        broadcast_list = []
        for k, v in self.__fib.items():
            if k == v[0]:
                broadcast_list.append(v)
        return broadcast_list