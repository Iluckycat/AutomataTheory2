import sys

sys.path.insert(0, '../SyntaxTree')
from SyntaxTree import Node


class Error_Handler:
    def __init__(self):
        self.type = None
        self.node = None
        self.types = self.types = ['UnexpectedError',
                                   'NoStartPoint',
                                   'UndeclaredError',
                                   'IndexError',
                                   'FuncCallError',
                                   'ValueError',
                                   'ApplicationCall',
                                   'TypeError']

    def call(self, error_type, node=None):
        self.type = error_type
        self.node = node
        sys.stderr.write(f'Error {self.types[int(error_type)]}:')
        if self.type == 0:
            pass
        if self.type == 1:
            sys.stderr.write(f'"main" function was not detected\n')
            return
        if self.type == 2:
            if node.type == 'assignment':
                sys.stderr.write(f'Variable for assignment at line '
                                 f'{self.node.value.lineno} is used before declaration\n')
        if self.type == 3:
            sys.stderr.write(f'List index is out of range at line '
                             f'{self.node.value.lineno}\n')
        if self.type == 4:
            sys.stderr.write(f'Unknown function call "{self.node.value}" at line '
                             f'{self.node.lineno} \n')
        if self.type == 5:
            if node.type == 'assignment':
                sys.stderr.write(f'Bad value for variable "{self.node.value.value}" at line '
                                 f'{self.node.value.lineno} \n')
        if self.type == 6:
            sys.stderr.write(f'Tried to call main function at line'
                             f' {self.node.lineno} \n')
        if self.type == 7:
            if node.type == 'assignment':
                sys.stderr.write(f'Bad values at assignment "{self.node.value.value}" at line '
                                 f'{self.node.value.lineno}\n')


class InterpreterUndeclaredError(Exception):
    pass


class InterpreterTypeError(Exception):
    pass


class InterpreterValueError(Exception):
    pass


class InterpreterApplicationCall(Exception):
    pass


class InterpreterIndexError(Exception):
    pass


class InterpreterNameError(Exception):
    pass
