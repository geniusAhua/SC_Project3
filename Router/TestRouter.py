import time
from CS import CS
from PIT import PIT
from FIB import FIB
from Router import PacketForward


class Data:
    def __init__(self):
        self.data = {}

    # Create a data packet
    @staticmethod
    def create_data(route_id, interest):
        """
        interest = {'type': 'interest', 'interest_ID': 0, 'consumer_ID': 0, 'route_ID': 0, 'content_name': 'r0/0',
                     'interest_hop': 0, 'life_hop': 5, 'run_start_time': 0.0, 'interest_start_time': 0.0, 'path': ''}
        data = {'type': 'data', 'consumer_ID': 0, 'route_ID': 0, 'content_name': 'r0/0', 'content_data': '',
                'data_hop': 0, 'run_start_time': 0.0, 'path': ''}
        """
        data = {'type': 'data', 'consumer_ID': interest['consumer_ID'], 'route_ID': route_id,
                'content_name': interest['content_name'], 'content_data': '', 'data_hop': 0, 'run_start_time': 0,
                'interest_start_time': 0, 'path': '', 'data_start_time': 0, 'interest_ID': interest['interest_ID']}
        content = interest['content_name'] + str(int(time.time()))
        data['content_data'] = content
        data['data_hop'] = 0
        data['run_start_time'] = interest['run_start_time']
        data['interest_start_time'] = interest['interest_start_time']
        data['path'] = 'p'
        data['data_start_time'] = time.process_time()
        return data

    # Pack the data packet to be sent and the output interface
    @staticmethod
    def send_data(infaces, route_id, data):
        """
        data = {'type': 'data', 'consumer_ID': 0, 'route_ID': 0, 'content_name': 'r0/0', 'content_data': '',
                'data_hop': 0, 'run_start_time': 0.0, 'path': ''}
        Infaces = [Inface, ...]
        data_list = [[Inface, data], ...]
        """
        data_list = []
        # Hop count plus 1
        data['data_hop'] += 1
        data['route_ID'] = route_id
        # Record the transmission path
        data['path'] += str(route_id) + '/'
        for i in range(len(infaces)):
            data_list.append([infaces[i], data])
        return data_list

    # data packet processing
    def on_data(self, device_name, sizes, route_id, data, tables, result_save, thread_lock):
        """
        data = {'type': 'data', 'consumer_ID': 0, 'route_ID': 0, 'content_name': 'r0/0', 'content_data': '',
                'data_hop': 0, 'run_start_time': 0.0, 'path': ''}
        sizes = [queue_size, cache_size, fib_size]
        tables = [self.network, self.cs, self.pit, self.fib]
        """
        content_store = CS(device_name)
        pending_interest_table = PIT(device_name)
        forward_information_base = FIB(device_name)
        forward = PacketForward()
        network, cs, pit, fib = tables
        _, cache_size, fib_size = sizes
        consumer_id = data['consumer_ID']
        # Check whether there is an entry matching the content name of the data packet in the pit
        pit_search_ack = pending_interest_table.find_pit_data(pit, data)
        # data match in PIT
        if pit_search_ack:
            content_store.cache_cs_data(cs, cache_size, data)
            forward_information_base.update_fib_outface_data(fib, route_id, fib_size, data)
            if consumer_id != route_id:
                infaces = forward.forward_data(device_name, pit, data)
                pending_interest_table.remove_pit_entry(pit, data)
                data_list = self.send_data(infaces, route_id, data)
                return data_list
            else:
                thread_lock.acquire()
                result_save['response_time'] += time.process_time() - data['interest_start_time']
                thread_lock.release()
                packet = []
                return packet
        else:
            content_store.cache_cs_data(cs, cache_size, data)
            forward_information_base.update_fib_outface_data(fib, route_id, fib_size, data)
            packet = []
            return packet


class Interest:
    def __init__(self):
        self.interest = {}
        self.interest_table = []

        # Consumer generated interest packet
    @staticmethod
    def generate_interest(route_id, run_start_time, interest, result_save, thread_lock):
        interests = []
        for i in range(0, len(interest)):
            interest_temp = {'type': 'interest', 'interest_ID': interest[i]['interest_ID'], 'consumer_ID': route_id,
                             'route_ID': route_id, 'content_name': interest[i]['content_name'], 'interest_hop': 0,
                             'life_hop': 12, 'run_start_time': run_start_time,
                             'interest_start_time': time.process_time(), 'path': 'p' + str(route_id) + '/'}
            interests.append(interest_temp)
            thread_lock.acquire()
            result_save["send_interest"] += 1
            thread_lock.release()
        return interests

    # Check whether the interest packet has timed out
    @staticmethod
    def time_out(interest, provider_save, thread_lock):
        interest_hop = interest['interest_hop']
        life_hop = interest['life_hop']
        if interest_hop < life_hop:
            return True
        else:
            # Drop interest
            return False

    # Pack the interest packet to be sent and the output interface
    @staticmethod
    def send_interest(device_name, pit, fib, outfaces, route_id, interest):
        """
        outfaces = [outface, ...]
        """
        # Send interest
        interests = []
        interest['route_ID'] = route_id
        interest['interest_hop'] += 1  # Hop count plus 1
        interest['path'] += str(route_id) + '/'  # Record the transmission path
        for i in range(len(outfaces)):  # Outfaces=[[outface,cost],...]
            outface = outfaces[i][0]
            interests.append([outface, interest])
        # outface is updated to pit
        pending_interest_table = PIT(device_name)
        pending_interest_table.update_pit_outface(pit, outfaces, interest)
        return interests

    # Interest packet processing
    def on_interest(self, device_name, route_id, interest, tables, sizes, result_save, thread_lock):
        content_store = CS(device_name)
        pending_interest_table = PIT(device_name)
        forward_information_base = FIB(device_name)
        da = Data()
        forwarding = PacketForward()
        inter = Interest()
        network, cs, pit, fib = tables
        _, cache_size, fib_size = sizes

        content_name = interest['content_name']

        # find interest packet in CS.
        search_cs_ack = content_store.find_cs_interest(cs, content_name)
        if search_cs_ack:  # interest hit in CS
            consumer_id = interest['consumer_ID']
            thread_lock.acquire()
            result_save['cache_hit_cs'] += 1
            thread_lock.release()
            if consumer_id == route_id:
                thread_lock.acquire()
                result_save['response_time'] += time.process_time() - interest['interest_start_time']
                thread_lock.release()
                packet = []
                return packet
            # Return data packet
            data = da.create_data(route_id, interest)
            inface = [interest['route_ID']]
            data_list = da.send_data(inface, route_id, data)
            return data_list
        else:
            thread_lock.acquire()
            result_save['cache_miss_cs'] += 1
            thread_lock.release()

        # Check whether there is an entry matching the content name of the interest packet in the pit
        search_pit_ack = pending_interest_table.find_pit_interest(pit, interest, route_id)
        # interest miss in PIT
        if search_pit_ack:
            # Forward the interest packet to the next router
            outfaces = forwarding.forward_interest(device_name, fib, network, route_id, interest)
            if len(outfaces) > 0:
                interests = self.send_interest(device_name, pit, fib, outfaces, route_id, interest)
                return interests
        packet = []
        return packet
