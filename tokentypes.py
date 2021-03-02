T_INTLIT = "INTLIT"
T_CHARLIT = "CHARLIT"
T_PLUS = "PLUS"
T_MINUS = "MINUS"
T_ASTERISK = "ASTERISK"
T_SLASH = "SLASH"
T_LEFTPAREN = "LEFTPAREN"
T_RIGHTPAREN = "RIGHTPAREN"
T_LEFTCURLY = "LEFTCURLY"
T_RIGHTCURLY = "RIGHTCURLY"
T_EQUALS = "EQUAL"
T_SEMICOLON = "SEMICOLON"
T_EOF = "EOF"
T_IDENTIFIER = "IDENTIFIER"
T_KEYWORD = "KEYWORD"
T_TYPE = "TYPE"

keywords = [
    "print",
]

types = [
    "int",
    "char",
    "void"
]


class Token(object):
    def __init__(self, _type, value, pos_start, pos_end=None):
        self.type = _type
        self.value = value
        self.pos_start = pos_start
        self.pos_end = pos_end
        if not self.pos_end:
            self.pos_end = self.pos_start.copy()
            self.pos_end.advance('')

    def match(self, _type, value):
        if self.type == _type and self.value == value:
            return True
        else:
            return False
    
    def __repr__(self):
        return f"TYPE: {self.type} & VALUE: {self.value}"
