class ContentStore:  # content - 'name':'data'
    def __init__(self, content):
        self._content = content

    def find_content_object(self, name):
        if name in self._content:
            return self._content[name]
        else:
            return None

    def add_content_object(self, content):
        if list(content.keys())[0] in self._content:
            return False
        else:
            self._content[list(content.keys())[0]] = list(content.values())[0]
            return self._content

    def remove_content_object(self, name):
        if name in self._content:
            self._content.pop(name)
            return self._content
        else:
            return False


class PendingInterestTable:  # entry - 'interest_name':'request_name'
    def __init__(self, entry):
        self._entry = entry

    def find_entry(self, interest_name):
        if interest_name in self._entry:
            return self._entry[interest_name]
        else:
            return None

    def add_entry(self, entry):
        if list(entry.keys())[0] in self._entry:
            return False
        else:
            self._entry[list(entry.keys())[0]] = list(entry.values())[0]
            return self._entry

    def remove_entry(self, interest_name):
        if interest_name in self._entry:
            self._entry.pop(interest_name)
            return self._entry
        else:
            return False


class RouterTable:
    def __init__(self, host, port, name):
        self.host = host
        self.port = port
        self.name = name

        self.map = {}  # name : ip mapping
        self.cs = {}
        self.pit = {}
        self.fib = {}


# cont = {
#     'name1': "This is message 1!",
#     'name2': 'This is message 2!',
#     'name3': 'This is message 3!',
#     'name4': 'This is message 4!',
# }
# cs = ContentStore(cont)
# print(cs.find_content_object('name1'))
# constant_ex = {'name5': 'This is message 5!'}
# print(cs.add_content_object(constant_ex))
# print(cs.remove_content_object('name5'))

ent = {
    'interest1': 'request1',
    'interest2': 'request2',
    'interest3': 'request3',
}
pit = PendingInterestTable(ent)
print(pit.find_entry('interest1'))
entry_ex = {'interest4': 'request4'}
print(pit.add_entry(entry_ex))
print(pit.remove_entry('interest4'))
