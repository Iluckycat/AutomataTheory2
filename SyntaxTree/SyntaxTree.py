class Node(object):
    # object constructor
    def __init__(self, t='const', val=None,  ch=None, no=None, pos=None):
        self.type = t
        self.value = val
        self.child = ch or []
        self.acc = None
        self.lineno = no
        self.lexpos = pos

    # object representation
    def __repr__(self):
        return f'{self.type} {self.value}'

    # print Tree
    def print(self, lvl=0):
        # offset
        if self is None:
            return
        print(' ' * lvl, self)
        if isinstance(self.child, list):
            for child in self.child:
                child.print(lvl + 1)
        elif isinstance(self.child, node):
            self.child.print(lvl + 1)
        elif isinstance(self.child, dict):
            for key, value in self.child.items():
                print(' ' * (lvl + 1), key)
                if value:
                    value.print(lvl + 2)