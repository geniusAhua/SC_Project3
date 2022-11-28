from PIT import PIT
from FIB import FIB


class PacketForward:
    def __init__(self):
        self.forward = 0

    # Get data packet forwarding interface
    @staticmethod
    def forward_data(device_name, pit, data):
        """
        data = {'type': 'data', 'consumer_ID': 0, 'route_ID': 0, 'content_name': 'r0/0', 'content_data': '',
                'data_hop': 0, 'run_start_time': 0.0, 'path': ''}
        pit = {'content_name': [[inface, ...], [outface, ...]], ...}
        """
        infaces = []
        inface = data['route_ID']
        # Get the requested content name of the data packet
        content_name = data['content_name']
        # Get the pit_entry of this content_name
        pending_interest_table = PIT(device_name)
        pit_entry = pit[content_name]   # pending_interest_table.get_pit_entry(content_name)
        for x in pit_entry[0]:
            if x != inface:
                infaces.append(x)
        return infaces

    # Get interest packet forwarding interface
    @staticmethod
    def forward_interest(device_name, fib, network, route_id, interest):
        outfaces = []
        inface = interest['route_ID']
        # Get the fibs record table of this router
        forward_information_base = FIB(device_name)
        outfaces = forward_information_base.find_fib_interest(fib, route_id, network, interest)
        return outfaces
