

class Test_print(object):
    def __init__(self):
        self._myonly = 7
    def add(self):
        self._myonly += 2
    def doit(self):
        print(self._myonly)

p = Test_print()
p.add()
p.add()
p.doit()