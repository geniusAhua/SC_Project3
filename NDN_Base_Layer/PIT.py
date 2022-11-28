class PIT():
    def __init__(self):
        self.__pit = {}

    def add_pit_item(self, dataname, outface, targetname):
        if dataname not in self.__pit:
            self.__pit[dataname] = []
        self.__pit[dataname].append([outface, targetname])

    def find_item(self, dataname):
        if dataname in self.__pit:
            return self.__pit[dataname]
        else: return 0

    def isExist(self, dataname):
        if dataname in self.__pit:
            return True
        else: return False

    def delete_pit_item(self, dataname):
        if dataname in self.__pit:
            del self.__pit[dataname]

    def get_pit(self):
        return self.__pit

    def get_outface(self, dataname):
        out = []
        if self.find_item(dataname):
            for item in self.__pit[dataname]:
                out.append(item[0])
    
    def get_targetname(self, dataname):
        return self.find_item(dataname)[0][1]
