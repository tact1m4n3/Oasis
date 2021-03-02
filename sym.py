D_NULL = 0
D_CHAR = 1
D_INT = 4

A_VARIABLE = 0
A_FUNCTION = 1

v_names = {
    D_CHAR: "char",
    D_INT: "int"
}


class GlobalContext:
    def __init__(self):
        self.parent = None
        self.symbols = {}

    def add_symbol(self, s):
        self.symbols[s.name] = s
        self.symbols[s.name].is_global = True

    def __repr__(self):
        return self.symbols.__repr__()


class FunctionContext:
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent

        self.symbols = {}

        self.align_count = 0
        self.last_symbol_offset = 0

        if parent:
            self.symbols.update(self.parent.symbols)

    def add_symbol(self, s):
        self.last_symbol_offset += s.data_type

        self.symbols[s.name] = s
        self.symbols[s.name].offset = self.last_symbol_offset

        if self.last_symbol_offset - self.align_count * 16 >= 0:
            self.align_count += 1
            return True
        return False

    def get_symbol(self, name):
        if name in self.symbols.keys():
            s = self.symbols[name]
        else:
            s = None

        return s

    def close_context(self):
        return self.parent

    def __repr__(self):
        return f"(STATIC {self.static_members} NONSTATIC {self.nonstatic_members})"


class Symbol:
    def __init__(self, name, _type, data_type):
        self.name = name
        self.type = _type
        self.data_type = data_type

        self.is_global = False
        self.offset = 0

    def set_offset(self, offset):
        self.offset = offset

    def __repr__(self):
        return f"NAME {self.name}, TYPE {self.data_type}"



