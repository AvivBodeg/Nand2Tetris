from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter
from CONSTANTS import *


class CompilationEngine:
    def __init__(self, input_file, output_file):
        self.tokenizer = JackTokenizer(input_file)
        self.symbol_table = SymbolTable()
        self.VMwriter = VMWriter(output_file)
        self.class_name = ''
        self.name = ''

    def advance(self):
        return self.tokenizer.advance()

    def double_peek(self, token):
        token_, value = self.tokenizer.deep_peek()
        self.VMwriter.write_arithmetic(token_)
        self.VMwriter.write_arithmetic(value)
        return token == token_

    def load_pointer(self, func_type):
        if func_type[1] == 'constructor':
            vars_count = self.symbol_table.count_variables_globally('field')
            self.VMwriter.write_push('constant', vars_count)
            self.VMwriter.write_call('Memory.alloc', 1)
            self.VMwriter.write_pop('pointer', 0)
        if func_type[1] == 'method':
            self.VMwriter.write_push('argument', 0)
            self.VMwriter.write_pop('pointer', 0)

    # CHECKERS
    def is_next_value_in_list(self, lst):
        token, value = self.tokenizer.peek()
        return value in lst

    def is_next_value(self, value):
        token, value_ = self.tokenizer.peek()
        return value == value_

    def is_next_token(self, token):
        token_, value = self.tokenizer.peek()
        return token_ == token

    def has_class_var_dec(self):
        return self.is_next_value('field') or self.is_next_value('static')

    def has_subroutine(self):
        return (self.is_next_value('constructor') or self.is_next_value('function')
                or self.is_next_value('method'))

    def has_var_dec(self):
        return self.is_next_value('var')

    def has_expression(self):
        # TODO: just remove, and use term
        return self.has_term_or_expression()

    def has_term_or_expression(self):
        return self.is_next_token('integerConstant') or self.is_next_token('stringConstant') \
            or self.is_next_token('identifier') or self.is_next_value('(')\
            or self.is_next_value_in_list(UNARY_OPERATORS) or self.is_next_value_in_list(KEYWORD_CONSTANTS)

    def has_parameter(self):
        return not self.is_next_token('symbol')

    def has_statement(self):
        return self.is_next_value_in_list(STATEMENTS)

    # COMPILERS
    def compile_class(self):
        """compiles a class"""
        self.advance()  # class
        self.class_name = self.advance()[1]
        self.advance()  # '{'
        if self.has_class_var_dec():
            self.compile_class_var_dec()
        while self.has_subroutine():
            self.compile_subroutine()
        self.advance()  # '}'

    def compile_class_var_dec(self):
        while self.has_class_var_dec():
            self.write_class_var_dec()

    def compile_subroutine(self):
        func_type = self.advance()
        self.advance()  # return type
        self.name = f'{self.class_name}.{self.advance()[1]}'
        self.symbol_table.reset(self.name)
        self.symbol_table.set_scope(self.name)
        self.advance()  # '('
        self.compile_parameter_list(func_type)
        self.advance()  # ')'
        self.compile_subroutine_body(func_type)

    def compile_subroutine_body(self, func_type):
        self.advance()  # '{'
        while self.has_var_dec():
            self.compile_var_dec()
        vars_count = self.symbol_table.count_variables('var')
        self.VMwriter.write_function(self.name, vars_count)
        self.load_pointer(func_type)
        self.compile_statements()
        self.advance()  # '}'
        self.symbol_table.set_scope(GLOBAL)

    def compile_statements(self):
        while self.has_statement():
            if self.is_next_value('let'):
                self.compile_let()
            elif self.is_next_value('do'):
                self.compile_do()
            elif self.is_next_value('while'):
                self.compile_while()
            elif self.is_next_value('if'):
                self.compile_if()
            elif self.is_next_value('return'):
                self.compile_return()

    def compile_parameter_list(self, func_type):
        if func_type[1] == 'method':
            self.symbol_table.define('this', 'self', 'arg')
        while self.has_parameter():
            self.write_parameter()

    def compile_expression_list(self):
        expression_counter = 0
        if self.has_expression():
            self.compile_expression()
            expression_counter += 1
        while self.is_next_value(','):
            self.advance()  # ','
            self.compile_expression()
            expression_counter += 1
        return expression_counter

    def compile_expression(self):
        self.compile_term()
        while self.is_next_value_in_list(BINARY_OPERATORS):
            operator = self.advance()[1]
            self.compile_term()
            if operator in ARITHMETIC_OPERATORS.keys():
                self.VMwriter.write_arithmetic(ARITHMETIC_OPERATORS[operator])
            elif operator == '*':
                self.VMwriter.write_call('Math.multiply', 2)
            elif operator == '/':
                self.VMwriter.write_call('Math.divide', 2)

    def compile_var_dec(self):
        kind = self.advance()[1]
        type_ = self.advance()[1]
        name = self.advance()[1]
        self.symbol_table.define(name, type_, kind)
        while self.is_next_value(','):
            self.advance()  # ','
            name = self.advance()[1]
            self.symbol_table.define(name, type_, kind)
        self.advance()  # ';'

    def compile_subroutine_call(self):
        locals_count = 0
        name = self.advance()[1]
        if self.is_next_value('.'):
            self.advance()  # ','
            sub_name = self.advance()[1]
            if name in self.symbol_table.current_scope or name in self.symbol_table.global_scope:
                self.write_push(name)
                full_name = f'{self.symbol_table.type_of(name)}.{sub_name}'
                locals_count += 1
            else:
                full_name = f'{name}.{sub_name}'
        else:
            self.VMwriter.write_push('pointer', 0)
            locals_count += 1
            full_name = f'{self.class_name}.{name}'
        self.advance()  # '('
        locals_count += self.compile_expression_list()
        self.VMwriter.write_call(full_name, locals_count)
        self.advance()  # ')'

    def compile_term(self):
        is_array = False
        if self.is_next_token("integerConstant"):
            value = self.advance()[1]
            self.VMwriter.write_push('constant', value)
        elif self.is_next_token("stringConstant"):
            value = self.advance()[1]
            self.VMwriter.write_push('constant', len(value))
            self.VMwriter.write_call('String.new', 1)
            for letter in value:
                self.VMwriter.write_push('constant', ord(letter))
                self.VMwriter.write_call('String.appendChar', 2)
        elif self.is_next_value_in_list(KEYWORD_CONSTANTS):
            value = self.advance()[1]
            if value == "this":
                self.VMwriter.write_push('pointer', 0)
            else:
                self.VMwriter.write_push('constant', 0)
                if value == "true":
                    self.VMwriter.write_arithmetic('not')
        elif self.is_next_token("identifier"):
            locals_count = 0
            name = self.advance()[1]
            if self.is_next_value("["):
                is_array = True
                self.compile_array_index(name)
            if self.is_next_value("("):
                locals_count += 1
                self.VMwriter.write_push('pointer', 0)
                self.advance()  # '('
                locals_count += self.compile_expression_list()
                self.advance()  # ')'
                self.VMwriter.write_call(f'{self.class_name}.{name}', locals_count)
            elif self.is_next_value("."):
                self.advance()  # '.'
                sub_name = self.advance()[1]
                if name in self.symbol_table.current_scope or name in self.symbol_table.global_scope:
                    self.write_push(name)
                    name = f'{self.symbol_table.type_of(name)}.{sub_name}'
                    locals_count += 1
                else:
                    name = f'{name}.{sub_name}'
                self.advance()  # '('
                locals_count += self.compile_expression_list()
                self.advance()  # ')'
                self.VMwriter.write_call(name, locals_count)
            else:
                if is_array:
                    self.VMwriter.write_pop('pointer', 1)
                    self.VMwriter.write_push('that', 0)
                elif name in self.symbol_table.current_scope:
                    if self.symbol_table.kind_of(name) == 'var':
                        self.VMwriter.write_push('local', self.symbol_table.index_of(name))
                    elif self.symbol_table.kind_of(name) == 'arg':
                        self.VMwriter.write_push('argument', self.symbol_table.index_of(name))
                else:
                    if self.symbol_table.kind_of(name) == 'static':
                        self.VMwriter.write_push('static', self.symbol_table.index_of(name))
                    else:
                        self.VMwriter.write_push('this', self.symbol_table.index_of(name))
        elif self.is_next_value_in_list(UNARY_OPERATORS):
            op = self.advance()[1]
            self.compile_term()
            if op == '-':
                self.VMwriter.write_arithmetic('neg')
            elif op == '~':
                self.VMwriter.write_arithmetic('not')
        elif self.is_next_value("("):
            self.advance()  # '('
            self.compile_expression()
            self.advance()  # ')'

    def compile_while(self):
        while_index = self.symbol_table.while_counter
        self.symbol_table.while_counter += 1
        self.VMwriter.write_label(f'WHILE{while_index}')
        self.advance()  # 'while'
        self.advance()  # '('
        self.compile_expression()
        self.VMwriter.write_arithmetic('not')
        self.VMwriter.write_if_goto(f'WHILE_END{while_index}')
        self.advance()  # ')'
        self.advance()  # '{'
        self.compile_statements()
        self.VMwriter.write_goto(f'WHILE{while_index}')
        self.VMwriter.write_label(f'WHILE_END{while_index}')
        self.advance()  # '}'

    def compile_return(self):
        self.advance()  # 'return'
        return_void = True
        while self.has_expression():
            self.compile_expression()
            return_void = False
        if return_void:
            self.VMwriter.write_push('constant', 0)
        self.VMwriter.write_return()
        self.advance()

    def compile_if(self):
        self.advance()  # 'if'
        self.advance()  # '('
        self.compile_expression()
        self.advance()  # ')'
        if_index = self.symbol_table.if_counter
        self.symbol_table.if_counter += 1
        self.VMwriter.write_if_goto(f'IF{if_index}')
        self.VMwriter.write_goto(f'IF_FALSE{if_index}')
        self.VMwriter.write_label(f'IF{if_index}')
        self.advance()  # '{'
        self.compile_statements()
        self.advance()  # '}'
        if self.is_next_value('else'):
            self.VMwriter.write_goto(f'IF_END{if_index}')
            self.VMwriter.write_label(f'IF_FALSE{if_index}')
            self.advance()  # 'else'
            self.advance()  # '{'
            self.compile_statements()
            self.advance()  # '}'
            self.VMwriter.write_label(f'IF_END{if_index}')
        else:
            self.VMwriter.write_label(f'IF_FALSE{if_index}')

    def compile_do(self):
        self.advance()  # 'do'
        self.compile_subroutine_call()
        self.VMwriter.write_pop('temp', 0)
        self.advance()  # ';'

    def compile_let(self):
        self.advance()  # 'let'
        is_array = False
        name = self.advance()[1]
        if self.is_next_value('['):
            is_array = True
            self.compile_array_index(name)
        self.advance()  # '='
        self.compile_expression()
        if is_array:
            self.VMwriter.write_pop('temp', 0)
            self.VMwriter.write_pop('pointer', 1)
            self.VMwriter.write_push('temp', 0)
            self.VMwriter.write_pop('that', 0)
        else:
            self.write_pop(name)
        self.advance()  # ';'

    def compile_array_index(self, name):
        self.write_array_index()
        self.write_push(name)
        self.VMwriter.write_arithmetic('add')

    # WRITES
    def write_class_var_dec(self):
        # TODO: replace with compile_vars_dec, duplicate possibly
        kind = self.advance()[1]
        type_ = self.advance()[1]
        name = self.advance()[1]
        self.symbol_table.define(name, type_, kind)
        while self.is_next_value(','):
            self.advance()  # ','
            name = self.advance()[1]
            self.symbol_table.define(name, type_, kind)
        self.advance()  # ';'

    def write_parameter(self):
        type_ = self.advance()[1]
        name = self.advance()[1]
        self.symbol_table.define(name, type_, 'arg')
        if self.is_next_value(','):
            self.advance()

    def write_array_index(self):
        self.advance()  # '['
        self.compile_expression()
        self.advance()  # ']'

    def write_push(self, name):
        if name in self.symbol_table.current_scope:
            if self.symbol_table.kind_of(name) == 'var':
                self.VMwriter.write_push('local', self.symbol_table.index_of(name))
            elif self.symbol_table.kind_of(name) == 'arg':
                self.VMwriter.write_push('argument', self.symbol_table.index_of(name))
        else:
            if self.symbol_table.kind_of(name) == 'static':
                self.VMwriter.write_push('static', self.symbol_table.index_of(name))
            else:
                self.VMwriter.write_push('this', self.symbol_table.index_of(name))

    def write_pop(self, name):
        if name in self.symbol_table.current_scope:
            if self.symbol_table.kind_of(name) == 'var':
                self.VMwriter.write_pop('local', self.symbol_table.index_of(name))
            elif self.symbol_table.kind_of(name) == 'arg':
                self.VMwriter.write_pop('argument', self.symbol_table.index_of(name))
        else:
            if self.symbol_table.kind_of(name) == 'static':
                self.VMwriter.write_pop('static', self.symbol_table.index_of(name))
            else:
                self.VMwriter.write_pop('this', self.symbol_table)
