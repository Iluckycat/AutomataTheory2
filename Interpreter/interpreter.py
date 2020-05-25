import os
import re
import sys
sys.path.insert(0, '../')
from Lexer.lexer_my import Lexer
from Parser.parser_my import Parser
from Errors.errors import Error_Handler
sys.path.insert(0, '../SyntaxTree')
from SyntaxTree import Node


class Variable:
    def __init__(self, value, index):
        self.index = index
        self.value = value
        if isinstance(self.value, int):
            self.type = 'int'
        elif (self.value == 'false') | (self.value == 'true'):
            self.type = 'bool'
        elif (self.value == 'EMPTY') | (self.value == 'WALL') | (self.value == 'BOX') | (self.value == 'EXIT') | (self.value == 'UNDEF'):
            self.type = 'cell'



# class Variable:
#     def __init__(self, *index,type, value):
#         self.value = dict()
#         if self.value.get(index) is None:
#             self.value[index] = 0
#         else:
#             tmp = {index: 0}
#             self.value.update(tmp)

class Interpreter:
    def __init__(self, parser=Parser()):
        self.parser = parser
        self.program = None
        self.symbol_table = dict()
        self.tree = None
        self.functions = None
        self.scope = 0
        self.robot = None
        self.exit = False
        self.correct = True
        self.error = Error_Handler()
        self.error_types = {'UnexpectedError': 0, }

    def interpreter(self, program=None, robot=None, tree_print=False):
        self.program = program
        self.robot = robot
        self.symbol_table = dict()
        self.tree, _ok, self.functions = self.parser.parse(self.program)
        if _ok:
            if tree_print:
                self.interpreter_tree(self.tree)
            self.interpreter_node(self.tree)
            return self.correct
        else:
            sys.stderr.write(f'Can\'t interpretate this program. Incorect syntax!\n')
            return False

    @staticmethod
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
            if node.value not in self.symbol_table:
                tmp = {node.value: 0}
                self.symbol_table.append(tmp)

        elif node.type == 'assignment':
            if self.symbol_table.get(node.children[0].value) is None:
                tmp_index = list()
                child = node.children[0].children
                if child.type == 'index':
                    tmp_index.append(child.value)
                    print(tmp_index)
                else:
                    child = child.children
                    while child[0].type != 'index':
                        tmp_index.append(child[1].value)
                        child = child[0].children
                    tmp_index.append(child[1].value)
                    tmp_index.append(child[0].value)
                    tmp_index.reverse()
                    print(tmp_index)
                tmp_smb = Variable(node.children[1].value, tmp_index)
                print()
                # tmp = {node.children[0].value: list.append(tmp_smb)}
        # elif node.type == 'assignment':
        #     if node.children[0].value not in self.symbol_table:
        #         tmp = {node.children[0].value: node.children[1].value}
        #         self.symbol_table.append(tmp)




# b = (1, 2, 3, 45, 89, 0, -5)
# a = Variable('true', b)
# print(a.value, '\n')
# print(a.index, '\n')
# print(a.type)
data = ''' n(1,2,3,5,9,7) <= 10;
           n(2) <= 20;
           m <= 20;'''

interpreter = Interpreter()
interpreter.interpreter(data)
print(interpreter.symbol_table)


