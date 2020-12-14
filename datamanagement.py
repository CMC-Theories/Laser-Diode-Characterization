import numpy as np
import os.path as path

class DataManagement:
    def __init__(self, fileArr,experiments, ILInd=0, IVInd = 1, LowInd=2,
                 AtInd=3, HighInd=4, IPInd = 5):
        self.files = fileArr
        self.indexing = [ILInd, IVInd, LowInd, AtInd, HighInd, IPInd]
        self.fileindex = [ind for ind in range(len(experiments))]
        self.reverseindex = {tuple(experiments[i]):i for i in range(len(experiments))}
        self._verifyFiles(printOutputs=False)
        self._loadFiles()
        self.extra_data = {i: {} for i in range(len(experiments))}
    def set_extra(self, mm, tmp, name, val):
        ind = self.reverseindex[(mm, tmp)]
        self.extra_data[self.fileindex[ind]][name] = val
    def get_extra(self, mm, tmp, name):
        ind = self.reverseindex[(mm, tmp)]
        return self.extra_data[self.fileindex[ind]][name]
    def __getitem__(self, index1):
        ind = self.reverseindex[(index1[0], index1[1])]
        if len(index1) == 4:
            if index1[3] not in self.extra_data[self.fileindex[ind]]:
                raise KeyError("No such key, \""+str(index1[3])+"\", in dictionary. All parameters: " + str(index1))
            return self.extra_data[self.fileindex[ind]][index1[3]]
        else:
            # Figure out which dataset to return
            return self._data[self.fileindex[ind]][self.indexing[index1[2]]]
    def __setitem__(self, index1, val):
        ind = self.reverseindex[(index1[0], index1[1])]
        if len(index1) == 4:
            self.extra_data[self.fileindex[ind]][index1[3]] = val
        else:
            raise IndexError("Not allowed to change read-only value.")
    def __delitem__(self, index1):
        ind = self.reverseindex[(index1[0], index1[1])]
        if len(index1) == 4:
            del self.extra_data[self.fileindex[ind]][index1[3]]
        else:
            raise IndexError("Not allowed to change read-only value.")
    def _verifyFiles(self, printOutputs=True):
        failed = False
        for i in self.files:
            for j in i:
                if not path.exists(j):
                    print("MISSING:", j)
                    failed = True
        if failed:
            raise Exception("There are missing files.")
        else:
            if printOutputs:
                print("All files present!")
            return True
    def _loadFiles(self):
        self._data = [[np.loadtxt(j, delimiter=",") for j in i] for i in self.files]
    