from Ttype import MemoryType


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
        self.global_memory = list()
        self.function_memory = list()
        self.lastGlobal = -1  # position of last "global" frame on stack - used to handle "special" case from labs
        self.inFunction = 0  # number of function calls on stack
        self.push(memory)

    def get(self, name):  # gets from memory stack current value of variable <name>
        in_function = False
        for mem in reversed(self.function_memory):
            if in_function:
                break
            elif mem.name == MemoryType.FUNCTION:
                in_function = True
            if mem.has_key(name):
                return mem.get(name)

        for mem in reversed(self.global_memory):
            if mem.has_key(name):
                return mem.get(name)

        return None

    def insert(self, name, value):  # inserts into memory stack variable <name> with value <value>
        self.get_memory_stack()[-1].put(name, value)

    def set(self, name, value):  # sets variable <name> to value <value>
        in_function = False
        for mem in reversed(self.function_memory):
            if in_function:
                break
            elif mem.name == MemoryType.FUNCTION:
                in_function = True
            if mem.has_key(name):
                mem.put(name, value)
                return

        for mem in reversed(self.global_memory):
            if mem.has_key(name):
                mem.put(name, value)
                break

    def push(self, memory):  # pushes memory <memory> onto the stack
        if memory.name == MemoryType.FUNCTION:
            self.function_memory.append(memory)
        else:
            self.get_memory_stack().append(memory)

    def pop(self):  # pops the top memory from the stack
        return self.get_memory_stack().pop()

    def get_memory_stack(self):
        return self.global_memory if len(self.function_memory) == 0 else self.function_memory
