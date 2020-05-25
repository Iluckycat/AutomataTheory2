import sys
sys.path.insert(0, '../SyntaxTree')
from SyntaxTree import Node

class Error_Handler:
    def __init__(self):
        self.type = None
        self.node = None
        self.types = self.types = ['UnexpectedError',
                                   'RedeclarationError',
                                   'UndeclaredError',]

    def call(self, error_type, node=None):
        self.type = error_type
        self.node = node
        sys.stderr.write(f'Error {self.types[int(error_type)]}')
        if self.type == 0:
            pass
        if self.type == 1:
            if isinstance(node.children, list):
                sys.stderr.write(f'Variable "{self.node.children[0].value}" at line {self.node.lineno} is already declared\n')
            else:
                sys.stderr.write(f'Variant "{self.node.children.value}" at line {self.node.lineno} is already declared\n')

