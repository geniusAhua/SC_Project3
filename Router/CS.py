import time


class CS:
    def __init__(self, device_name):
        self.device_name = device_name
        self.cs = []  # [[entry1], [entry2], ...]
        self.cs_entry = []  # [content_name, data, time, cost]

    def cs(self, route_id):
        return self.cs

    def get_cs(self, route_id):
        return self.cs

    @staticmethod
    def find_cs_interest(cs, content_name):
        for cs_entry in cs:
            if content_name == cs_entry[0]:
                # cs_entry[-1] += 1
                return True
        return False  # No data for content name found in cs

    @staticmethod
    # Check if there is data matching the content name in ps
    def find_ps_interest(ps, content_name):  # ps = [content_name,...]
        for i in range(len(ps)):
            if content_name == ps[i]:
                return True
        # No data for content name found in ps
        return False

    @staticmethod
    def add_cs_entry(data, cs):
        """
        cs = [[content_name, data, time, cost],...]
        cs_entry = [content_name, data, time, cost]
        data = {'type': 'data', 'consumer_ID': 0, 'route_ID': 0, 'content_name': 'r0/0', 'content_data': '',
                'data_hop': 0, 'run_start_time': 0.0, 'path': ''}
        """
        content_name = data['content_name']
        content_data = data['content_data']
        # Record the time this entry was created
        times = int(time.process_time()*1000 - data['run_start_time'])
        cost = data['data_hop']
        cs_entry = [content_name, content_data, times, cost]
        cs.append(cs_entry)
        return cs_entry

    @staticmethod
    def remove_cs_entry(cs):  # remove the most cost entry
        """
        cs = [[content_name, data, time, cost],...]
        """
        cs.sort(key=lambda x: (x[3]), reverse=True)  # sort cs according to the cost from high to low
        del cs[0]

    def cache_cs_data(self, cs, cache_size, data):
        """
        cs = [[content_name, data, time, cost],...]
        data = {'type': 'data', 'consumer_ID': 0, 'route_ID': 0, 'content_name': 'r0/0', 'content_data': '',
                'data_hop': 0, 'run_start_time': 0.0, 'path': ''}
        """
        content_name = data['content_name']
        if self.find_cs_interest(cs, content_name):  # check if this entry in the cs
            return
        if len(cs) > cache_size:  # if the CS cache is full, remove the most costly entry
            self.remove_cs_entry(cs)
        self.add_cs_entry(data, cs)  # then add the new entry
