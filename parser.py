from tokentypes import *
from nodetypes import *
from error import Error

PREC_EOF = 0
PREC_ASSIGN = 10
PREC_COMPARISON = 20
PREC_UNARY = 30
PREC_PLUSMINUS = 40
PREC_MULDIV = 50


class Parser(object):
    def __init__(self, toks):
        self.toks = toks
        
        self.current_tok = None
        self.idx = -1

        self.error: bool = False

        self.advance()

    def advance(self):
        self.idx += 1
        self.current_tok = self.toks[self.idx] if self.idx < len(self.toks) else None

    """
    Global context
    """
    def parse_file(self):
        stmts = GlobalStatements()

        while self.current_tok.type is not T_EOF and not self.error:
            if self.check_eof():
                return
            stmt = self.parse_global_statement()
            stmts.append(stmt)

        return stmts

    def parse_global_statement(self):
        if self.current_tok.type == T_TYPE:
            node = self.parse_global_symbol()
            return node
        else:
            self.error = True
            err = Error("Expected symbol declaration", self.current_tok.pos_start, self.current_tok.pos_end)
            print(err.as_string())
            return

    def parse_global_symbol(self):
        """
        Parsing class attribute or method
        :return: Node
        """

        pos_start = self.current_tok.pos_start

        var_type = self.current_tok
        if var_type.type != T_TYPE:
            self.error = True
            err = Error("Expected type of variable", self.current_tok.pos_start, self.current_tok.pos_end)
            print(err.as_string())
            return

        self.advance()

        ident = self.current_tok
        if ident.type != T_IDENTIFIER:
            self.error = True
            err = Error("Expected identifier", self.current_tok.pos_start, self.current_tok.pos_end)
            print(err.as_string())
            return

        self.advance()

        if self.current_tok.type == T_LPAREN:
            args = ()
            self.advance()
            if self.current_tok.type != T_RPAREN:
                self.error = True
                err = Error("Expected ')'", self.current_tok.pos_start, self.current_tok.pos_end)
                print(err.as_string())
                return

            self.advance()

            if self.current_tok.type != T_LCURLY:
                if self.current_tok.type != T_SEMICOLON:
                    self.error = True
                    err = Error("Expected ';'", self.current_tok.pos_start, self.current_tok.pos_end)
                    print(err.as_string())
                    return
                self.advance()
                return FunctionDeclarationNode(var_type, ident, args, None,
                                       pos_start, self.current_tok.pos_end)

            self.advance()
            stmts = self.parse_function_stmts()

            return FunctionDeclarationNode(var_type, ident, args, stmts, pos_start,
                                              self.current_tok.pos_end)
        else:
            if self.current_tok.type != T_SEMICOLON:
                self.error = True
                err = Error("Expected ';'", self.current_tok.pos_start, self.current_tok.pos_end)
                print(err.as_string())
                return

            self.advance()

            return GlobalVarDeclarationNode(var_type, ident, pos_start, self.current_tok.pos_end)

    """
    Function related functions
    """
    def parse_function_stmts(self):
        stmts = FunctionStatements()

        while self.current_tok.type is not T_RCURLY and not self.error:
            if self.check_eof():
                return
            stmt = self.parse_function_stmt()
            stmts.append(stmt)

        self.advance()

        return stmts

    def parse_function_stmt(self):
        pos_start = self.current_tok.pos_start

        if self.current_tok.match(T_KEYWORD, "print"):
            self.advance()
            expr = self.parse_expr(0)
            if self.check_semi():
                return
            self.advance()

            return PrintNode(expr, pos_start, self.current_tok.pos_end)
        elif self.current_tok.type == T_TYPE:
            node = self.parse_local_symbol()
            return node
        else:
            expr = self.parse_expr(0)
            if self.check_semi():
                return
            self.advance()

            return expr
    
    def parse_local_symbol(self):
        pos_start = self.current_tok.pos_start

        var_type = self.current_tok
        if var_type.type != T_TYPE:
            self.error = True
            err = Error("Expected type of variable", self.current_tok.pos_start, self.current_tok.pos_end)
            print(err.as_string())
            return

        self.advance()

        ident = self.current_tok
        if ident.type != T_IDENTIFIER:
            self.error = True
            err = Error("Expected identifier", self.current_tok.pos_start, self.current_tok.pos_end)
            print(err.as_string())
            return

        self.advance()

        if self.current_tok.type == T_EQ:
            self.advance()

            expr = self.parse_expr(20)
            if self.check_semi():
                return
            
            self.advance()
            return LocalVarDeclarationNode(var_type, ident, expr, pos_start, self.current_tok.pos_end)
        else:
            if self.current_tok.type != T_SEMICOLON:
                self.error = True
                err = Error("Expected ';'", self.current_tok.pos_start, self.current_tok.pos_end)
                print(err.as_string())
                return

            self.advance()

            return LocalVarDeclarationNode(var_type, ident, None, pos_start, self.current_tok.pos_end)

    """
    Math expressions
    """
    def parse_expr(self, prec):
        left = self.parse_primary()

        tokentype = self.current_tok.type
        if tokentype == T_SEMICOLON or tokentype == T_RPAREN or tokentype == T_EOF:
            return left

        while self.get_precedence(tokentype) >= prec:
            self.advance()
            right = self.parse_expr(self.get_precedence(tokentype))

            if tokentype == T_EQ:
                if type(left) == IdentifierNode:
                    left = VarAssignNode(left, right, left.pos_start, right.pos_end)
                else:
                    self.error = True
                    err = Error("Expected identifier", left.pos_start, left.pos_end)
                    print(err.as_string())
                    return
            else:
                left = BinaryOperationNode(left, tokentype, right, left.pos_start, right.pos_end)

            tokentype = self.current_tok.type
            if tokentype == T_SEMICOLON or tokentype == T_RPAREN or tokentype == T_EOF:
                return left

        return left

    def parse_primary(self):
        if self.current_tok.type == T_INTLIT:
            node = IntLitNode(self.current_tok.value, self.current_tok.pos_start, self.current_tok.pos_end)
            self.advance()
            return node
        elif self.current_tok.type == T_CHARLIT:
            node = CharLitNode(self.current_tok.value, self.current_tok.pos_start, self.current_tok.pos_end)
            self.advance()
            return node
        elif self.current_tok.type == T_IDENTIFIER:
            node = IdentifierNode(self.current_tok, self.current_tok.pos_start, self.current_tok.pos_end)
            self.advance()
            return node
        elif self.current_tok.type == T_MINUS:
            pos_start = self.current_tok.pos_start

            sign = self.current_tok.type
            self.advance()
            val = self.parse_primary()
            node = UnaryOperationNode(sign, val, pos_start, self.current_tok.pos_end)
            return node
        elif self.current_tok.type == T_LPAREN:
            self.advance()
            expr = self.parse_expr(0)
            if self.current_tok.type != T_RPAREN:
                self.error = True
                err = Error("Expected ')'", self.current_tok.pos_start, self.current_tok.pos_end)
                print(err.as_string())
                return

            self.advance()

            return expr

        self.error = True
        err = Error("Expected int", self.current_tok.pos_start, self.current_tok.pos_end)
        print(err.as_string())

    """
    Utils
    """
    def get_precedence(self, tokentype):
        if tokentype == T_EOF:
            return PREC_EOF
        elif tokentype == T_EQ:
            return PREC_ASSIGN
        elif tokentype == T_DEQ:
            return PREC_COMPARISON
        elif tokentype == T_NEQ:
            return PREC_COMPARISON
        elif tokentype == T_LT:
            return PREC_COMPARISON
        elif tokentype == T_LTE:
            return PREC_COMPARISON
        elif tokentype == T_GT:
            return PREC_COMPARISON
        elif tokentype == T_GTE:
            return PREC_COMPARISON
        elif tokentype == T_INTLIT:
            return PREC_UNARY
        elif tokentype == T_PLUS:
            return PREC_PLUSMINUS
        elif tokentype == T_MINUS:
            return PREC_PLUSMINUS
        elif tokentype == T_ASTERISK:
            return PREC_MULDIV
        elif tokentype == T_SLASH:
            return PREC_MULDIV
        else:
            self.error = True
            err = Error("Syntax error", self.current_tok.pos_start, self.current_tok.pos_end)
            print(err.as_string())
            return -1

    def check_semi(self):
        if self.current_tok.type != T_SEMICOLON:
            self.error = True
            err = Error("Expected ';'", self.current_tok.pos_start, self.current_tok.pos_end)
            print(err.as_string())
            return 1
        return 0

    def check_eof(self):
        if self.current_tok.type == T_EOF:
            self.error = True
            err = Error("EOF Error", self.current_tok.pos_start, self.current_tok.pos_end)
            print(err.as_string())
            return 1
        return 0
