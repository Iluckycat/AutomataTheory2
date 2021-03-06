import os
import re
import sys

sys.path.insert(0, '../')
from Lexer.lexer_my import Lexer
from Parser.parser_my import Parser
from Errors.errors import Error_Handler
from Errors.errors import InterpreterApplicationCall
from Errors.errors import InterpreterIndexError
from Errors.errors import InterpreterNameError
from Errors.errors import InterpreterValueError
from Errors.errors import InterpreterTypeError
from Errors.errors import InterpreterFuncCallError
from Robot.robot import Robot, Cell, cells

sys.path.insert(0, '../SyntaxTree')
from SyntaxTree import Node


class Variable:
    def __init__(self, value, index):
        self.index = index
        if (value == 'false') | (isinstance(value, bool) and value == False):
            self.types = 'bool'
            self.value = False
        elif (value == 'true') | (isinstance(value, bool) and value == True):
            self.types = 'bool'
            self.value = True
        elif isinstance(value, int):
            self.types = 'int'
            self.value = value

        elif (value == 'EMPTY') | (value == 'WALL') | (value == 'BOX') | (value == 'EXIT') | (value == 'UNDEF'):
            self.types = 'cell'
            self.value = value
        else:
            self.value = value
            self.types = 'int'

    def __repr__(self):
        return f'{self.types} {self.index} {self.value}'


class TypeConversion:
    def __init__(self):
        pass

    def converse(self, type, var1, index):
        if type == var1.type:
            return var1
        elif type == 'bool':
            if var1.type == 'int':
                return self.int_to_bool(var1, index)
            elif var1.type == 'cell':
                return self.cell_to_bool(var1, index)
        elif type == 'int':
            if var1.type == 'bool':
                return self.bool_to_int(var1, index)
        elif type == 'cell':
            if var1.type == 'bool':
                return self.bool_to_cell(var1, index)
        elif type.find(var1.type) != -1:
            return Variable(var1.value, index)

    @staticmethod
    def cell_to_bool(var1, index):
        if (var1.value == 'EMPTY') | (var1.value == 'WALL') | (var1.value == 'BOX') | (var1.value == 'EXIT') | (
                var1.value == 'UNDEF'):
            return Variable('true', index)
        elif var1.value == 'UNDEF':
            return Variable('false', index)

    @staticmethod
    def bool_to_cell(var1, index):
        if not var1.value:
            return Variable('UNDEF', index)

    @staticmethod
    def int_to_bool(var1, index):
        if var1.value == 0:
            return Variable(False, index)
        else:
            return Variable(True, index)

    @staticmethod
    def bool_to_int(var1, index):
        if var1.value:
            return Variable(1, index)
        else:
            return Variable(0, index)


class Interpreter:
    def __init__(self, parser=Parser(), converter=TypeConversion()):
        self.parser = parser
        self.converter = converter
        self.map = None
        self.program = None
        self.symbol_table = [dict()]
        self.tree = None
        self.functions = None
        self.scope = 0
        self.robot = None
        self.exit = False
        self.error = Error_Handler()
        self.error_types = {'UnexpectedError': 0,
                            'NoStartPoint': 1,
                            'UndeclaredError': 2,
                            'IndexError': 3,
                            'FuncCallError': 4,
                            'ValueError': 5,
                            'ApplicationCall': 6,
                            'TypeError': 7}

    def interpreter(self, program=None, robot=None):
        self.program = program
        self.robot = robot
        self.symbol_table = [dict()]
        self.tree, _ok, self.functions = self.parser.parse(self.program)
        if _ok:
            if 'main' not in self.functions.keys():
                print(self.error.call(self.error_types['NoStartPoint']))
                return
            self.interpreter_tree(self.tree)
            try:
                self.interpreter_node(self.functions['main'].children['body'])
                return True
            except RecursionError:
                sys.stderr.write(f'RECURSIONERROR : Function recursion calls to many times\n')
                sys.stderr.write("------- Program was finished with fatal error -------\n")
                return False
        else:
            sys.stderr.write(f'Can\'t interpretate this program. Incorect syntax!\n')


    def interpreter_tree(self, tree):
        print("Program tree:\n")
        tree.print()
        print('\n')

    def interpreter_node(self, node):
        if node is None:
            return
        #  unexpected error
        if node.type == 'error':
            self.error.call
        # program
        if node.type == 'program':
            self.interpreter_node(node.children)
        # program -> statements
        elif node.type == 'statements':
            for child in node.children:
                self.interpreter_node(child)
        # program -> statemetns ->statement
        elif node.type == 'statement':
            self.interpreter_node(node.children)
        # program -> statements -> statement -> assignment

        elif node.type == 'variable':
            if self.scope == 0:
                fl = False
                if node.value in self.symbol_table[self.scope].keys():
                    tmp = self.list_of_ind(node)
                    for i in self.symbol_table[self.scope][node.value]:
                        if tmp == i.index:
                            fl = True
                            return i.value
                else:
                    raise InterpreterNameError
                if not fl:
                    raise InterpreterIndexError
            else:
                c = self.scope
                fl1 = False
                fl2 = False
                while c >= 0:
                    if node.value in self.symbol_table[c].keys():
                        fl2 = True
                        tmp = self.list_of_ind(node)
                        for i in self.symbol_table[c][node.value]:
                            if tmp == i.index:
                                fl1 = True
                                return i.value
                    c -= 1
                if not fl2:
                    raise InterpreterNameError
                if not fl1:
                    raise InterpreterIndexError
        elif node.type == 'var':
            if self.scope == 0:
                if node.value in self.symbol_table[self.scope].keys():
                    return self.symbol_table[self.scope][node.value]
                else:
                    raise InterpreterNameError
            else:
                c = self.scope
                while c >= 0:
                    if node.value in self.symbol_table[c].keys():
                        return self.symbol_table[c][node.value]
                    c -= 1
                raise InterpreterNameError

        elif node.type == 'const':
            try:
                tmp = float(node.value)
                tmp = int(tmp)
            except Exception:
                if node.value == 'true':
                    tmp = True
                elif node.value == 'false':
                    tmp = False
                else:
                    return node.value
            return tmp

        elif node.type == 'operation':
            if node.value == '+':
                try:
                    return self.binar_plus(self.interpreter_node(node.children[0]), self.interpreter_node(node.children[1]))
                except InterpreterTypeError:
                    print(self.error.call(self.error_types['TypeError'], node))
                    sys.exit()
            if node.value == '-':
                try:
                    return self.binar_minus(self.interpreter_node(node.children[0]),
                                            self.interpreter_node(node.children[1]))
                except InterpreterTypeError:
                    print(self.error.call(self.error_types['TypeError'], node))
                    sys.exit()
        elif node.type == 'un_operation':
            tmp = self.interpreter_node(node.children)
            try:
                return self.unar_minus(tmp)
            except InterpreterTypeError:
                print(self.error.call(self.error_types['TypeError'], node))
                sys.exit()
        elif node.type == 'assignment':
            val = node.children[0].value
            try:
                tmp_index = self.list_of_ind(node.children[0])
            except:
                print(self.error.call(self.error_types[IndexError], node))
                sys.exit()
            if self.scope == 0:
                if val not in self.symbol_table[self.scope].keys():
                    if node.children[0].type == 'variable':
                        self.symbol_table[self.scope][val] = [Variable(self.interpreter_node(node.children[1]), tmp_index), ]
                    elif node.children[0].type == 'var' and node.children[1].type == 'var':
                        self.symbol_table[self.scope][val] = self.interpreter_node(node.children[1])
                    elif node.children[0].type == 'var' and isinstance(self.interpreter_node(node.children[1]), list):
                        v = self.interpreter_node(node.children[1])
                        j = 0
                        for i in v:
                            self.symbol_table[self.scope][val] = [Variable(i, j), ]
                            j += 1
                else:
                    if node.children[0].type == 'variable':
                        fl = False
                        tmp = 0
                        for i in self.symbol_table[self.scope][val]:
                            if tmp_index == i.index:
                                fl = True
                                tmp = i
                        if fl:
                            try:
                                tmp.value = self.interpreter_node(node.children[1])
                            except InterpreterNameError:
                                print(self.error.call(self.error_types['UndeclaredError'], node))
                                sys.exit()
                            except InterpreterIndexError:
                                print(self.error.call(self.error_types['IndexError'], node))
                                sys.exit()
                            except InterpreterTypeError:
                                print(self.error.call(self.error_types['TypeError'], node))
                                sys.exit()
                        else:
                            try:
                                self.add_in_tab(Variable(self.interpreter_node(node.children[1]), tmp_index), val)
                            except InterpreterNameError:
                                print(self.error.call(self.error_types['UndeclaredError'], node))
                                sys.exit()
                            except InterpreterIndexError:
                                print(self.error.call(self.error_types['IndexError'], node))
                                sys.exit()
                            except InterpreterTypeError:
                                print(self.error.call(self.error_types['TypeError'], node))
                                sys.exit()
                    elif node.children[0].type == 'var' and node.children[1].type == 'var':
                        self.symbol_table[self.scope][val] = self.interpreter_node(node.children[1])
                    elif node.children[0].type == 'var' and isinstance(self.interpreter_node(node.children[1]), list):
                        v = self.interpreter_node(node.children[1])
                        j = 0
                        for i in v:
                            self.symbol_table[self.scope][val][j] = Variable(i, j)
                            j += 1

            else:
                ct = 0
                fl = False
                fl2 = False
                tmp = 0
                while ct <= self.scope:
                    if val in self.symbol_table[ct].keys():
                        for i in self.symbol_table[ct][val]:
                            if tmp_index == i.index:
                                fl = True
                                tmp = i
                                break
                            if fl:
                                try:
                                    tmp.value = self.interpreter_node(node.children[1])
                                except InterpreterNameError:
                                    print(self.error.call(self.error_types['UndeclaredError'], node))
                                    sys.exit()
                                except InterpreterIndexError:
                                    print(self.error.call(self.error_types['IndexError'], node))
                                    sys.exit()
                                except InterpreterTypeError:
                                    print(self.error.call(self.error_types['TypeError'], node))
                                    sys.exit()
                                fl2 = True
                                break
                        ct += 1
                    if not fl2:
                        if val not in self.symbol_table[self.scope].keys():
                            self.symbol_table[self.scope][val] = [Variable(self.interpreter_node(node.children[1]), tmp_index),]
                        else:
                            try:
                                self.add_in_tab(Variable(self.interpreter_node(node.children[1]), tmp_index), val)
                            except InterpreterNameError:
                                print(self.error.call(self.error_types['UndeclaredError'], node))
                                sys.exit()
                            except InterpreterIndexError:
                                print(self.error.call(self.error_types['IndexError'], node))
                                sys.exit()
                            except InterpreterTypeError:
                                print(self.error.call(self.error_types['TypeError'], node))
                                sys.exit()
        elif node.type == 'logic_expr':
            if node.value == '&':
                if node.children[0].type == 'variable' and node.children[1].type == 'variable':
                    return self.interpreter_node(node.children[0]) and self.interpreter_node(node.children[1])
                else:
                    print(self.error.call(self.error_types['TypeError'], node))
                    sys.exit()
            elif node.value == '/':
                if node.children[0].type == 'variable' and node.children[1].type == 'variable':
                    return self.interpreter_node(node.children[0]) | self.interpreter_node(node.children[1])
                else:
                    print(self.error.call(self.error_types['TypeError'], node))
                    sys.exit()
            elif node.value == 'in':
                if (node.children[0].type == 'variable' or node.children[0].type == 'const') and node.children[
                    1].type == 'variable':
                    if self.interpreter_node(node.children[0]) == self.interpreter_node(node.children[1]):
                        return True
                    else:
                        return False

                elif (node.children[0].type == 'variable' or node.children[0].type == 'const') and node.children[
                    1].type == 'var':
                    for i in self.symbol_table[self.scope][node.children[1].value]:
                        if self.interpreter_node(node.children[0]) == i.value:
                            return True
                    return False
                else:
                    print(self.error.call(self.error_types['TypeError'], node))
                    sys.exit()
            elif node.value == 'all in':
                if node.children[0].type == 'var' and node.children[1].type == 'var':
                    fl = 0
                    for i in self.symbol_table[self.scope][node.children[0].value]:
                        for j in self.symbol_table[self.scope][node.children[1].value]:
                            if i.value == j.value:
                                fl += 1
                                break
                    if fl == len(self.symbol_table[self.scope][node.children[0].value]):
                        return True
                    else:
                        return False
                else:
                    print(self.error.call(self.error_types['TypeError'], node))
                    sys.exit()
            elif node.value == 'some in':
                if node.children[0].type == 'var' and node.children[1].type == 'var':
                    fl = 0
                    for i in self.symbol_table[self.scope][node.children[0].value]:
                        for j in self.symbol_table[self.scope][node.children[1].value]:
                            if i.value == j.value:
                                fl += 1
                                break
                    if fl > 0:
                        return True
                    else:
                        return False
                else:
                    print(self.error.call(self.error_types['TypeError'], node))
                    sys.exit()
            elif node.value == 'less':
                if (node.children[0].type == 'variable' or node.children[0].type == 'const') and node.children[
                    1].type == 'variable':
                    if self.interpreter_node(node.children[0]) < self.interpreter_node(node.children[1]):
                        return True
                    else:
                        return False
                elif (node.children[0].type == 'variable' or node.children[0].type == 'const') and node.children[
                    1].type == 'var':
                    fl = 0
                    for i in self.symbol_table[self.scope][node.children[1].value]:
                        if self.interpreter_node(node.children[0]) < i.value:
                            fl += 1
                        if fl == len(self.symbol_table[self.scope][node.children[1].value]):
                            return True
                        else:
                            return False
                else:
                    print(self.error.call(self.error_types['TypeError'], node))
                    sys.exit()
            elif node.value == 'all less':
                if node.children[0].type == 'var' and node.children[1].type == 'var':
                    fl = 0
                    for i in self.symbol_table[self.scope][node.children[0].value]:
                        for j in self.symbol_table[self.scope][node.children[1].value]:
                            if i.value > j.value:
                                fl += 1
                                break
                        if fl == len(self.symbol_table[self.scope][node.children[0].value]):
                            return False
                        else:
                            return True
            elif node.value.type == 'variable':
                val = self.interpreter_node(node.value)
                if val == 0:
                    return False
                else:
                    return True
            else:
                print(self.error.call(self.error_types['TypeError'], node))
                sys.exit()

        elif node.type == 'if':
            cond = False
            try:
                cond = self.interpreter_node(node.children[0])
            except InterpreterValueError:
                print(self.error.call(self.error_types['TypeError'], node))
                sys.exit()
            except InterpreterNameError:
                print(self.error.call(self.error_types['UndeclaredError'], node))
                sys.exit()
            except InterpreterIndexError:
                print(self.error.call(self.error_types['IndexError'], node))
                sys.exit()
            if cond:
                self.interpreter_node(node.children[1])
        elif node.type == 'from_cycle':
            try:
                self.op_from(node)
            except InterpreterNameError:
                print(self.error.call(self.error_types['UndeclaredError'], node))
                sys.exit()
            except InterpreterIndexError:
                print(self.error.call(self.error_types['IndexError'], node))
                sys.exit()
            except InterpreterTypeError:
                print(self.error.call(self.error_types['TypeError'], node))
                sys.exit()
        elif node.type == 'from_cycle_ws':
            try:
                self.op_from(node)
            except InterpreterNameError:
                print(self.error.call(self.error_types['UndeclaredError'], node))
                sys.exit()
            except InterpreterIndexError:
                print(self.error.call(self.error_types['IndexError'], node))
                sys.exit()
            except InterpreterTypeError:
                print(self.error.call(self.error_types['TypeError'], node))
                sys.exit()
        elif node.type == 'function_call':
            try:
                return self.function_call(node)
            except InterpreterApplicationCall:
                print(self.error.call(self.error_types['ApplicationCall'], node))
                sys.exit()
            except InterpreterFuncCallError:
                print(self.error.call(self.error_types['FuncCallError'], node))
                sys.exit()
            # if node.children.value in self.functions.keys():
            #     self.scope += 1
            #     self.symbol_table.append(dict())
            #     body = self.functions[node.children.value].children['body']
            #     self.interpreter_node(body)
            #     if body.children[1] == 'variable' or body.children[1] == 'var' or body.children[1] == 'const':
            #         val = self.interpreter_node(body.children[1])
            #         self.scope -= 1
            #         self.symbol_table.pop()
            #         return val
            #     else:
            #         self.scope -= 1
            #         self.symbol_table.pop()
            # else:
            #     print(self.error.call(self.error_types['FuncCallError'], node))
            #     sys.exit()
        elif node.type == 'function':
            pass
        elif node.type == 'command':
            if node.value == 'go':
                res = self.go(node.children)
            elif node.value == 'pick':
                res = self.pick(node.children)
            elif node.value == 'drop':
                res = self.drop(node.children)
            else:
                res = self.look(node.children)
            return res

    def binar_plus(self, val1, val2):
        if isinstance(val1, int) and isinstance(val2, int):
            return val1 + val2
        else:
            raise InterpreterTypeError

    def binar_minus(self, val1, val2):
        if isinstance(val1, int) and isinstance(val2, int):
            return val1 - val2
        else:
            raise InterpreterTypeError

    def unar_minus(self, val1):
        if isinstance(val1, bool):
            return not val1
        elif isinstance(val1, int):
            return -val1
        else:
            raise InterpreterTypeError

    def getType(self, val):
        if isinstance(val, bool):
            tmp_type = 'bool'
        elif isinstance(val, int):
            tmp_type = 'int'
        else:
            tmp_type = 'cell'
        return tmp_type

    def add_in_tab(self, val, name):
        if self.symbol_table[self.scope][name][0].types == val.types:
            self.symbol_table[self.scope][name].append(val)
        else:
            raise InterpreterTypeError

    def list_of_ind(self, node):
        tmp_index = list()
        child = node.children
        if child.type == 'null_index':
            tmp_index.append('0')
        elif child.type == 'index':
            tmp_index.append(child.value)
        else:
            child = child.children
            while child[0].type != 'index':
                tmp_index.append(child[1].value)
                child = child[0].children
            tmp_index.append(child[1].value)
            tmp_index.append(child[0].value)
            tmp_index.reverse()
        return tmp_index

    def op_from(self, node):
        f = self.interpreter_node(node.children['from'])
        t = self.interpreter_node(node.children['to'])
        if not (isinstance(f, int) and isinstance(t,int)):
            raise InterpreterTypeError
        if node.type == 'from_cycle':
            step = 1
        else:
            step = self.interpreter_node(node.children['with_step'])
            if not isinstance(step, int):
                raise InterpreterTypeError
        if step > 0:
            while f < t:
                try:
                    self.interpreter_node(node.children['body'])
                except Exception:
                    self.interpreter_node(node.children['call'])
                f += step
        elif step < 0:
            while f > t:
                try:
                    self.interpreter_node(node.children['body'])
                except Exception:
                    self.interpreter_node(node.children['call'])
                f += step

    def check_index(self, node):
        index = self.list_of_ind(node)
        for i in self.symbol_table[self.scope][node.value]:
            if index == i.index:
                return True
            else:
                return False

    def function_call(self, node):
        if node.children.value == 'main':
            raise InterpreterApplicationCall
        if node.children.value in self.functions.keys():
            self.scope += 1
            if self.scope > 75:
                self.scope -= 1
                raise RecursionError from None
            self.symbol_table.append(dict())
            body = self.functions[node.children.value].children['body']
            self.interpreter_node(body)
            if body.children[1] == 'variable' or body.children[1] == 'var' or body.children[1] == 'const':
                var = self.interpreter_node(body.children[1])
                self.scope -= 1
                self.symbol_table.pop()
                return var
            else:
                self.scope -= 1
                self.symbol_table.pop()
        else:
            raise InterpreterFuncCallError

    def go(self, children):
        return self.robot.go(children.value)

    def pick(self, children):
        return self.robot.pick(children.value)

    def drop(self, children):
        return self.robot.drop(children.value)

    def look(self, children):
        return self.robot.look(children.value)

    



data = ''' function fibonachi
x(3) <= x(1) + x()
x(1) <= x()
x() <= x(3)
end
function main
x() <= 0
x(1) <= 3
x(2) <= 4
from x(2) - 2 to 0 with step -1 do fibonachi
end
           '''

interpreter = Interpreter()
interpreter.interpreter(data)
print(interpreter.symbol_table)
