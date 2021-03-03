class GlobalStatements(list):
    pass


class FunctionStatements(list):
    pass


class IntLitNode(object):
    def __init__(self, value, pos_start, pos_end):
        self.value = value

        self.pos_start = pos_start
        self.pos_end = pos_end
    
    def __repr__(self):
        return str(self.value)


class CharLitNode(object):
    def __init__(self, value, pos_start, pos_end):
        self.value = value
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return str(self.value)


class IdentifierNode(object):
    def __init__(self, value, pos_start, pos_end):
        self.value = value

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return repr(self.value)


class UnaryOperationNode(object):
    def __init__(self, sign, right_node, pos_start, pos_end):
        self.sign = sign
        self.right_node = right_node

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"( {self.sign} {self.right_node} )"


class BinaryOperationNode(object):
    def __init__(self, left_node, sign, right_node, pos_start, pos_end):
        self.left_node = left_node
        self.sign = sign
        self.right_node = right_node

        self.pos_start = pos_start
        self.pos_end = pos_end
    
    def __repr__(self):
        return f"( {self.left_node} {self.sign} {self.right_node} )"


class PrintNode(object):
    def __init__(self, expr, pos_start, pos_end):
        self.expr = expr

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"PRINT {self.expr}"


class GlobalVarDeclarationNode(object):
    def __init__(self, type_, name, pos_start, pos_end):
        self.type = type_
        self.name = name

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"VAR {repr(self.name)} TYPE {self.type}"

class LocalVarDeclarationNode(object):
    def __init__(self, type_, name, initial, pos_start, pos_end):
        self.type = type_
        self.name = name
        self.initial = initial

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"VAR {self.name} = {self.initial}"

class VarAssignNode(object):
    def __init__(self, name, expr, pos_start, pos_end):
        self.name = name
        self.expr = expr
        
        self.pos_start = pos_start
        self.pos_end = pos_end
    
    def __repr__(self):
        return f"{self.name} = {self.expr}"

class IfNode(object):
    def __init__(self, expr, if_stmts, else_stmts, pos_start, pos_end):
        self.expr = expr
        self.if_stmts = if_stmts
        self.else_stmts = else_stmts

        self.pos_start = pos_start
        self.pos_end = pos_end
    
    def __repr__(self):
        return f"(IF ({self.expr}) {self.if_stmts} ELSE {self.else_stmts})"

class FunctionDeclarationNode(object):
    def __init__(self, type_, name, args, stmts, pos_start, pos_end):
        self.type = type_
        self.name = name
        self.args = args
        self.stmts = stmts
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"FUNCTION {self.name}({self.args}) {self.stmts}"

