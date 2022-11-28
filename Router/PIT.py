class PIT:
    def __init__(self, device_name):
        self.device_name = device_name
        self.pit = {}  # pit = {'content_name': [[inface, ...], [outface, ...]]}
        self.pit_entry = []

    # Each router creates an independent pit table
    def pit(self, route_id):
        return self.pit

    def get_pit(self):
        return self.pit

    # find the entry of the content name from the pit
    @staticmethod
    def find_pit_entry(pit, content_name):
        pit_entry = pit[content_name]
        return pit_entry

    # update outface to pit
    @staticmethod
    def update_pit_outface(pit, outfaces, interest):
        """
        interest = {'type': 'interest', 'interest_ID': 0, 'consumer_ID': 0, 'route_ID': 0, 'content_name': 'r0/0',
                    'interest_hop': 0, 'life_hop': 5, 'start_time': 0.0}
        pit = {'content_name': [[inface, ...], [outface, ...]], ...}
        Outfaces = [outface, ...]
        pit_entry = [[inface, ...], [outface, ...]]
        """
        content_name = interest['content_name']
        # Check whether there is a record of an entry with the same name as the interest packet in the PIT
        pit_entry = pit[content_name]
        for outface in outfaces:        # Outfaces=[[Outface, cost],...]
            pit_entry[1].append(outface[0])   # append outface to pit_entry[[inface, ...], [outface, ...]]
        # Remove duplicate inface
        pit_entry[1] = list(set(pit_entry[1]))
        pit[content_name] = pit_entry

    # The inface of the received interest packet is merged into the same content name
    def merge_pit_entry(self, pit, interest, route_id):
        """
        interest = {'type': 'interest', 'interest_ID': 0, 'consumer_ID': 0, 'route_ID': 0, 'content_name': 'r0/0',
                    'interest_hop': 0, 'life_hop': 5, 'start_time': 0.0}
        pit = {'content_name': [[inface, ...], [outface, ...]], ...}
        """
        inface = interest['route_ID']
        content_name = interest['content_name']
        pit_entry = self.find_pit_entry(pit, content_name)
        pit_entry[0].append(inface)
        # Remove duplicate inface
        pit_entry[0] = list(set(pit_entry[0]))

    # Create a pit entry
    @staticmethod
    def add_pit_entry(pit, interest, route_id):
        """
        interest = {'type': 'interest', 'interest_ID': 0, 'consumer_ID': 0, 'route_ID': 0, 'content_name': 'r0/0',
                    'interest_hop': 0, 'life_hop': 5, 'start_time': 0.0}
        pit = {'content_name': [[inface, ...], [outface, ...]], ...}
        """
        inface = interest['route_ID']
        content_name = interest['content_name']
        new_dict = {content_name: [[inface], []]}
        pit.update(new_dict)

    # Check whether there is an entry matching the content name of the interest packet in the pit
    def find_pit_interest(self, pit, interest, route_id):
        """
        interest = {'type': 'interest', 'interest_ID': 0, 'consumer_ID': 0, 'route_ID': 0, 'content_name': 'r0/0',
                    'interest_hop': 0, 'life_hop': 5, 'start_time': 0.0}
        pit = {'content_name': [[inface, ...], [outface, ...]], ...}
        """
        # Get the requested content name of the interest packet
        content_name = interest['content_name']
        # Check whether there is a record of an entry with the same name as the interest packet in the PIT
        if content_name in pit:
            # The inface of the received interest packet is merged into the same content name
            self.merge_pit_entry(pit, interest, route_id)
            return False
        else:
            # Create a pit entry
            self.add_pit_entry(pit, interest, route_id)
            return True

    # Check whether there is an entry matching the content name of the data packet in the pit
    @staticmethod
    def find_pit_data(pit, data):
        """
        data = {'type': 'data', 'consumer_ID': 0, 'route_ID': 0, 'content_name': 'r0/0', 'content_data': '',
                'data_hop': 0, 'start_time': 0.0}
        pit = {'content_name': [[inface, ...], [outface, ...]], ...}
        """
        # Get the requested content name of the interest packet
        content_name = data['content_name']
        # Check whether there is a record of an entry with the same name as the interest packet in the PIT
        if content_name in pit:
            return True
        else:
            return False

    # The content_name entry is removed from pit
    @staticmethod
    def remove_pit_entry(pit, data):
        """
        pit = {'content_name': [[inface, ...], [outface, ...]], ...}
        """
        content_name = data['content_name']
        # remove content_name entry in pit
        del pit[content_name]
