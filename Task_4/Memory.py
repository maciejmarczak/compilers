# memory types
FUN_MEM = 'fun_mem'
GLOBAL_MEM = 'global_mem'
COMPOUND_MEM = 'compound_mem'


class Memory:
    def __init__(self, name):  # memory name
        self.name = name
        self.variables = dict()

    def has_key(self, name):  # variable name
        return name in self.variables

    def get(self, name):  # gets from variables current value of variable <name>
        return self.variables[name]

    def put(self, name, value):  # puts into variables current value of variable <name>
        self.variables[name] = value


class MemoryStack:
    def __init__(self, memory):  # initialize memory stack with memory <memory>
        self.global_mem = list()
        self.fun_mem = list()
        self.recursion_level = 0  # number of function calls on stack
        self.push(memory)

    def get(self, name):  # gets from memory stack current value of variable <name>
        el = self.find_in_stack(self.fun_mem, name)
        return el if el is not None else self.find_in_stack(self.global_mem, name)

    def insert(self, name, value):  # inserts into memory stack variable <name> with value <value>
        self.mem_stack()[-1].put(name, value)

    def set(self, name, value):  # sets variable <name> to value <value>
        if self.set_in_stack(self.fun_mem, name, value):
            return
        else:
            self.set_in_stack(self.global_mem, name, value)

    def push(self, memory):  # pushes memory <memory> onto the stack
        if memory.name == FUN_MEM:
            self.fun_mem.append(memory)
        else:
            self.mem_stack().append(memory)

    def pop(self):  # pops the top memory from the stack
        return self.mem_stack().pop()

    # if we're currently inside a fun stack, return it; otherwise return global memory
    def mem_stack(self):
        if len(self.fun_mem) > 0:
            return self.fun_mem
        else:
            return self.global_mem

    @staticmethod
    def find_in_stack(stack, name):
        for mem in reversed(stack):
            if mem.has_key(name):
                return mem.get(name)
            if mem.name == FUN_MEM:
                break
        return None

    @staticmethod
    def set_in_stack(stack, name, value):
        for mem in reversed(stack):
            if mem.has_key(name):
                mem.put(name, value)
                return True
            if mem.name == FUN_MEM:
                break
        return False
