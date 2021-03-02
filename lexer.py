from tokentypes import *
from error import Error
from string import ascii_letters

DIGITS = "01231456789"
LETTERS = ascii_letters


class Position(object):
    def __init__(self, col, idx, line, filename, filetext):
        self.col = col
        self.idx = idx
        self.line = line
        self.filename = filename
        self.filetext = filetext
    
    def advance(self, current_char):
        self.idx += 1
        self.col += 1
        if current_char == '\n':
            self.line += 1
            self.col = 0
    
    def copy(self):
        return Position(self.col, self.idx, self.line, self.filename, self.filetext)


class Lexer:
    def __init__(self, filename):
        self.filename = filename
        with open(filename, 'r') as f:
            self.filetext = f.read()
        
        self.position = Position(-1, -1, 0, self.filename, self.filetext)
        self.current_char = None
        self.putback = None

        self.error: bool = False

        self.advance()
    
    def advance(self):
        if self.putback:
            c = self.putback
            self.putback = None
            return c
        self.position.advance(self.current_char)
        self.current_char = self.filetext[self.position.idx] if self.position.idx < len(self.filetext) else None
    
    def make_tokens(self):
        tokens = []
        
        while self.current_char:
            if self.current_char in ' \t\n':
                self.advance()
                continue
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in LETTERS + '_':
                tokens.append(self.make_identifier())
            elif self.current_char == '\'':
                pos_start = self.position.copy()
                self.advance()
                char = self.current_char
                self.advance()

                if self.current_char != '\'':
                    self.error = True
                    pos_end = self.position.copy()
                    pos_end.advance('')
                    err = Error("You forgot an apostroph :))", self.position.copy(), pos_end)
                    print(err.as_string())
                else:
                    pos_end = self.position.copy()
                    pos_end.advance('')

                    tokens.append(Token(T_CHARLIT, ord(char), pos_start, pos_end))
            elif self.current_char == '+':
                tokens.append(Token(T_PLUS, None, self.position.copy()))
            elif self.current_char == '-':
                tokens.append(Token(T_MINUS, None, self.position.copy()))
            elif self.current_char == '*':
                tokens.append(Token(T_ASTERISK, None, self.position.copy()))
            elif self.current_char == '/':
                tokens.append(Token(T_SLASH, None, self.position.copy()))
            elif self.current_char == '(':
                tokens.append(Token(T_LEFTPAREN, None, self.position.copy()))
            elif self.current_char == ')':
                tokens.append(Token(T_RIGHTPAREN, None, self.position.copy()))
            elif self.current_char == '{':
                tokens.append(Token(T_LEFTCURLY, None, self.position.copy()))
            elif self.current_char == '}':
                tokens.append(Token(T_RIGHTCURLY, None, self.position.copy()))
            elif self.current_char == '=':
                tokens.append(Token(T_EQUALS, None, self.position.copy()))
            elif self.current_char == ';':
                tokens.append(Token(T_SEMICOLON, None, self.position.copy()))
            else:
                self.error = True
                pos_end = self.position.copy()
                pos_end.advance('')
                err = Error("Invalid character", self.position.copy(), pos_end)
                print(err.as_string())
            
            self.advance()

        tokens.append(Token(T_EOF, None, self.position))
        
        return tokens
    
    def make_number(self):
        pos_start = self.position.copy()
        number = 0
        while self.is_number(self.current_char):
            number = number * 10 + int(self.current_char)
            self.advance()
        
        self.putback = self.current_char
        
        return Token(T_INTLIT, number, pos_start, self.position.copy())

    def make_identifier(self):
        pos_start = self.position.copy()
        ident = ""
        while self.is_letter(self.current_char):
            ident += self.current_char
            self.advance()

        self.putback = self.current_char

        if self.is_keyword(ident):
            return Token(T_KEYWORD, ident, pos_start, self.position.copy())
        elif self.is_type(ident):
            return Token(T_TYPE, ident, pos_start, self.position.copy())
        else:
            return Token(T_IDENTIFIER, ident, pos_start, self.position.copy())

    @staticmethod
    def is_number(num):
        if not num:
            return 0
        if num in DIGITS:
            return 1
        return 0

    @staticmethod
    def is_letter(c):
        if not c:
            return 0
        if c in LETTERS + '_':
            return 1
        return 0

    @staticmethod
    def is_keyword(ident):
        if ident in keywords:
            return True
        return False

    @staticmethod
    def is_type(ident):
        if ident in types:
            return True
        return False
