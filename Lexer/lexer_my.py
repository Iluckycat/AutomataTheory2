import sys
import ply.lex as lex

reserved = {

    # CYCLE
    'from': 'FROM',
    'to': 'TO',
    'with': 'WITH',
    'step': 'STEP',
    # IF
    'if': 'IF',
    # FUNCTION
    'main': 'MAIN',
    'function': 'FUNCTION',
    'end': 'END',
    'do': 'DO'
}


class Lexer:
    def __init__(self):
        self.lexer = lex.lex(module=self)

    tokens = ['BOOL', 'CELLTYPE', 'CMP', 'CMD',
              'INT', 'FLOAT', 'NAME',
              'LBRACKET', 'RBRACKET',
              'ASSIGNMENT', 'PLUS',
              'MINUS', 'AND', 'OR', 'ANY',
              'NEWLINE', 'SEMICOLON',
              'COMMA', 'DIRECT'] + list(reserved.values())

    t_ignore = '[ ]|\t'

    def t_ASSIGNMENT(self,t):
        r'\<='
        return t

    def t_PLUS(self, t):
        r'\+'
        return t

    def t_MINUS(self, t):
        r'\-'
        return t

    def t_AND(self, t):
        r'\&'
        return t

    def t_OR(self, t):
        r'\|'
        return t

    def t_COMMA(self, t):
        r'\,'
        return t

    def t_LBRACKET(self, t):
        r'\('
        return t

    def t_RBRACKET(self, t):
        r'\)'
        return t

    def t_SEMICOLON(self, t):
        r'\;'
        return t

    def t_BOOL(self, t):
        r'true|false'
        return t

    def t_CELLTYPE(self, t):
        r'EMPTY|WALL|BOX|EXIT|UNDEF'
        return t

    def t_CMP(self, t):
        r'((all|some)[ ]+(in|less))|in|less'
        return t

    def t_CMD(self, t):
        r'go|pick|look|drop'
        return t

    def t_DIRECT(self, t):
        r'left|right|down|up'
        return t

    def t_NAME(self, t):
        r'\_?[a-zA-Z][\w]*'
        t.type = reserved.get(t.value, 'NAME')
        return t

    def t_FLOAT(self, t):
        r'[0-9]+\.[0-9]*'
        return t

    def t_INT(self, t):
        r'[0-9]+'
        return t

    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        return t

    def t_ANY(self, t):
        r'.+'
        return t

    def t_error(self, t):
        sys.stderr.write(f'Illegal character: {t.value[0]} at line {t.lexer.lineno}\n')
        t.lexer.skip(1)

    def input(self, data):
        return self.lexer.input(data)

    def token(self):
        return self.lexer.token()


data = ''' n <= 10 
           r <= 2
        function multiplay from 1 to n do function n <= r; r <= r + n end end 
         do multiplay
         ''' \
       'a <= 10;' \
       'from a to 20 with step 1 do function ' \
       'a <= a + 1;' \
       'go up & pick left & drop right;' \
       'end;' \
       'if a less 20 do function go down end;' \
       '- some in all in  some less all less false EMPTY WALL BOX EXIT UNDEF CELL | drop 0.234'
lexer = Lexer()
lexer.input(data)
while True:
    token = lexer.token()
    if token is None:
        break
    else:
        print(token)
