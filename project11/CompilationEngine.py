from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter
from CONSTANTS import UNARY_OPERATORS, KEYWORD_CONSTANTS, GLOBAL, BINARY_OPERATORS, ARITHMETIC_OPERATORS


class CompilationEngine:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.tokenizer = JackTokenizer(input_file)
        self.symbol_table = SymbolTable()
        self.VMwriter = VMWriter(output_file)
        self.name = ''
        self.class_name = ''

    def advance(self):
        return self.tokenizer.advance()

    # VALUE/TOKEN CHECKS:
    def is_next_val_in_list(self, lst):
        """ checks if the next value is in the list"""
        token, val = self.tokenizer.peek()
        return val in lst

    def is_next_val(self, value):
        """ checks if the next value is the one supplied"""
        token, val = self.tokenizer.peek()
        return val == value

    def is_next_token(self, token):
        """ checks if the next token is the one supplied"""
        toke, val = self.tokenizer.peek()
        return toke == token

    def deep_peek(self, token):
        """ checks if the next next token is the one supplied"""
        toke, val = self.tokenizer.deep_peek()
        return toke == token

    # EXISTS CHECKERS
    def has_class_variables(self):
        """ checks if the class has a field/static declaration"""
        return (self.is_next_val('static')
                or self.is_next_val('field'))

    def has_subroutine(self):
        return (self.is_next_val('constructor')
                or self.is_next_val('method') or self.is_next_val('function'))

    def has_parameter(self):
        return not self.is_next_token('symbol')

    def has_val_dec(self):
        return self.is_next_val('var')

    def has_statement(self):
        return (self.is_next_val('do')
                or self.is_next_val('if')
                or self.is_next_val('while')
                or self.is_next_val('let')
                or self.is_next_val('return')
                )

    def term_exists(self):
        return (self.is_next_token('integerConstant')
                or self.is_next_token('stringConstant')
                or self.is_next_token('identifier')
                or self.is_next_val_in_list(UNARY_OPERATORS)
                or self.is_next_val_in_list(KEYWORD_CONSTANTS)
                or self.is_next_val('(')
                )

    # COMPILERS
    def compile_class(self):
        """ Compiles a class"""
        self.advance()  # 'class'
        self.class_name = self.advance()[1]
        self.advance()  # '{'
        if self.has_class_variables():
            self.compile_class_variables()
        while self.has_subroutine():
            self.compile_subroutine()
        self.advance()  # '}'

    def compile_subroutine(self):
        """ compiles a method/function/constructor"""
        function_type = self.advance()  # method/function/constructor
        self.name = f'{self.class_name}.{self.advance()[1]}'
        self.symbol_table.reset(self.name)
        self.symbol_table.set_scope(self.name)
        self.advance()  # '('
        self.compile_parameter_list(function_type)
        self.advance()  # ')'
        self.compile_subroutine_body(function_type)

    def compile_class_variables(self):
        """ Compiles the static and field declarations"""
        while self.has_class_variables():
            self.write_class_var_dec()

    def compile_parameter_list(self, function_type):
        """ compiles a list of parameters, possibly empty"""
        if function_type[1] == 'method':
            self.symbol_table.define('this', 'self', 'arg')
        while self.has_parameter():
            self.write_parameter()

    def compile_subroutine_body(self, function_type):
        self.advance()  # '{'
        while self.has_val_dec():
            self.compile_var_dec()
        num_vars = self.symbol_table.count_variables('var')
        self.VMwriter.write_function(self.name, num_vars)
        self.load_pointer(function_type)
        self.compile_statements()
        self.advance()  # '}'
        self.symbol_table.set_scope(GLOBAL)

    def compile_var_dec(self):
        """" compiles a variable declaration"""
        kind = self.advance()[1]  # 'var'
        type_ = self.advance()[1]  # type
        name = self.advance()[1]  # var_name
        self.symbol_table.define(name, kind, type_)
        while self.is_next_val(','):
            self.advance()  # ','
            name = self.advance()[1]  # var_name
            self.symbol_table.define(name, kind, type_)
        self.advance()  # ';'

    def compile_subroutine_call(self):
        """ compiles subroutine call. do name([list])"""
        num_locals = 0
        name = self.advance()[1]   # class/subroutine/variable name
        if self.is_next_val(','):
            self.advance()  # ','
            sub_subroutine_name = self.advance()[1]   # subroutine name
            if name in self.symbol_table.current_scope or name in self.symbol_table.global_scope:
                self.VMwriter.write_push(name, sub_subroutine_name)
                full_name = f'{self.symbol_table.type_of(name)}.{sub_subroutine_name}'
                num_locals += 1
            else:
                full_name = f'{name}.{sub_subroutine_name}'
        else:
            self.VMwriter.write_push('pointer', 0)
            num_locals += 1
            full_name = f'{self.class_name}.{name}'
        self.advance()  # '('
        num_locals += self.compile_expression_list()
        self.VMwriter.write_call(full_name, num_locals)
        self.advance()  # ')'

    def compile_expression_list(self):
        """compiles a list of experssion, possibly empty and returns the amount of expressions"""
        expression_counter = 0
        if self.term_exists():
            self.compile_expression()
            expression_counter += 1
        while self.is_next_val(','):
            self.advance()  # ','
            self.compile_expression()
            expression_counter += 1
        return expression_counter

    def compile_expression(self):
        """ compiles an expression"""
        self.compile_term()
        while self.is_next_val_in_list(BINARY_OPERATORS):
            operator = self.advance()[1]  # op_symbol
            self.compile_term()
            if operator in ARITHMETIC_OPERATORS.keys():
                self.VMwriter.write_arithmetic(ARITHMETIC_OPERATORS[operator])
            elif operator == '*':
                self.VMwriter.write_call('Math.multiply', 2)
            elif operator == '/':
                self.VMwriter.write_call('Math.divide', 2)

    # TODO: remake this somehow, its awful
    def compile_term(self):
        """ compiles term"""
        is_array = False
        if self.is_next_token("integerConstant"):
            value = self.advance()[1]  # constant
            self.VMwriter.write_push('constant', value)
        elif self.is_next_token("stringConstant"):
            value = self.advance()[1]  # string
            self.VMwriter.write_push('constant', len(value))
            self.VMwriter.write_call('String.new', 1)
            for letter in value:
                self.VMwriter.write_push('constant', ord(letter))
                self.VMwriter.write_call('String.appendChar', 2)
        elif self.is_next_val(KEYWORD_CONSTANTS):
            value = self.advance()[1]  # keywordConstant
            if value == "this":
                self.VMwriter.write_push('pointer', 0)
            else:
                self.VMwriter.write_push('constant', 0)
                if value == "true":
                    self.VMwriter.write_arithmetic('not')
        elif self.is_next_token("identifier"):
            nLocals = 0
            name = self.advance()[1]  # class/var/func name
            if self.is_next_val("["):  # case of varName[expression]
                is_array = True
                self.compile_array_index(name)
            if self.is_next_val("("):
                nLocals += 1
                self.VMwriter.write_push('pointer', 0)
                self.advance()  # '('
                nLocals += self.compile_expression_list()
                self.advance()  # ')'
                self.VMwriter.write_call(self.class_name + '.' + name, nLocals)
            elif self.is_next_val("."):  # case of subroutine call
                self.advance()  # '.'
                lastName = self.advance()[1]  # subroutine name
                if name in self.symbol_table.current_scope or name in self.symbol_table.global_scope:
                    self.write_push(name)
                    name = self.symbol_table.type_of(name) + '.' + lastName
                    nLocals += 1
                else:
                    name = name + '.' + lastName
                self.advance()  # '('
                nLocals += self.compile_expression_list()
                self.advance()  # ')'
                self.VMwriter.write_call(name, nLocals)
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
        elif self.is_next_val(UNARY_OPERATORS):
            op = self.advance()[1]  # unary op
            self.compile_term()
            if op == '-':
                self.VMwriter.write_arithmetic('neg')
            elif op == '~':
                self.VMwriter.write_arithmetic('not')
        elif self.is_next_val("("):
            self.advance()  # '('
            self.compile_expression()
            self.advance()  # ')'

    def compile_array_index(self, name):    # DONE
        self.write_array_index()
        self.write_push(name)
        self.VMwriter.write_arithmetic('add')

    def compile_statements(self):
        """ compiles a list of statements"""
        while self.has_statement():
            if self.is_next_val("do"):
                self.compile_do()
            elif self.is_next_val("while"):
                self.compile_while()
            elif self.is_next_val("return"):
                self.compile_return()
            elif self.is_next_val("let"):
                self.compile_let()
            elif self.is_next_val("if"):
                self.compile_if()

    # STATEMENTS:
    def compile_let(self):
        """ compiles let statement"""
        self.advance()  # let
        is_array = False
        name = self.advance()[1]    # var_name
        if self.is_next_val('['):  # array
            is_array = True
            self.compile_array_index()
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

    # TODO: ########################## here
    def compile_if(self):   # DONE
        """ compiles if statement"""
        self.advance()  # if
        self.advance()  # '('
        self.compile_expression()
        self.advance()  # ')'
        self.advance()  # '{'
        # setup jumps
        jump_index = self.symbol_table.if_counter
        self.symbol_table.if_counter += 1
        self.VMwriter.write_if_goto(f'if_true{jump_index}')
        self.VMwriter.write_goto(f'if_false{jump_index}')
        self.VMwriter.write_label(f'if_true{jump_index}')
        self.compile_statements()
        self.advance()  # '}'
        if self.is_next_val('else'):
            self.advance()  # else
            self.advance()  # '{'
            # setup jumps
            self.VMwriter.write_goto(f'if_end{jump_index}')
            self.VMwriter.write_label(f'if_false{jump_index}')
            self.compile_statements()
            self.advance()  # '}'
            self.VMwriter.write_label(f'if_end{jump_index}')
        else:
            self.VMwriter.write_label(f'if_false{jump_index}')

    def compile_do(self):   # DONE
        """ compiles do statement"""
        self.advance()  # do
        self.compile_subroutine_call()
        self.VMwriter.write_pop('temp', 0)
        self.advance()  # ';'

    def compile_while(self):    # DONE
        """ compiles while statement"""
        self.advance()  # while
        self.advance()  # '('
        jump_index = self.symbol_table.while_counter
        self.symbol_table.while_counter += 1
        # setup jumps
        self.VMwriter.write_label(f'while{jump_index}')
        self.compile_expression()
        self.advance()  # ')'
        self.advance()  # '{'
        self.VMwriter.write_arithmetic('not')
        self.VMwriter.write_if_goto(f'while_end{jump_index}')
        self.compile_statements()
        self.advance()  # '}'
        self.VMwriter.write_label(f'while{jump_index}')
        self.VMwriter.write_label(f'while_end{jump_index}')

    def compile_return(self):   # done
        """ compiles return statement :)"""
        self.advance()  # return
        return_void = not self.term_exists()
        while self.term_exists():
            self.compile_expression()
        self.advance()  # ';'
        if return_void:
            self.VMwriter.write_push('constant', 0)
        self.VMwriter.write_return()

    # WRITES DONE
    def write_parameter(self):
        """writes a single parameter, with option to add ',' if there are multiple"""
        self.advance()  # type
        self.advance()  # param_name
        if self.is_next_val(','):
            self.advance()  # ','

    def write_array_index(self):
        """ writes array index in the form '[term]' """
        self.advance()  # '['
        self.compile_expression()
        self.advance()  # ']'

    def write_class_var_dec(self):
        """ writes a class variable in the form of <static|field> <type> var_name* """
        self.advance()  # static/field
        self.advance()  # type
        self.advance()  # var_name
        while self.is_next_val(','):
            self.advance()  # ','
            self.advance()  # var_name
        self.advance()  # ';'

    def write_push(self, name):
        if name in self.symbol_table.current_scope:
            if self.symbol_table.kind_of(name) == 'arg':
                self.VMwriter.write_pop('argument', self.symbol_table.index_of(name))
            elif self.symbol_table.kind_of(name) == 'var':
                self.VMwriter.write_pop('local', self.symbol_table.index_of(name))
        else:
            if self.symbol_table.kind_of(name) == 'static':
                self.VMwriter.write_pop('static', self.symbol_table.index_of(name))
            else:
                self.VMwriter.write_pop('this', self.symbol_table.index_of(name))

    def write_pop(self, name):
        if name in self.symbol_table.current_scope:
            if self.symbol_table.kind_of(name) == 'arg':
                self.VMwriter.write_push('argument', self.symbol_table.index_of(name))
            elif self.symbol_table.kind_of(name) == 'var':
                self.VMwriter.write_push('local', self.symbol_table.index_of(name))
        else:
            if self.symbol_table.kind_of(name) == 'static':
                self.VMwriter.write_push('static', self.symbol_table.index_of(name))
            else:
                self.VMwriter.write_push('this', self.symbol_table.index_of(name))

    def load_pointer(self, function_type):
        if function_type[1] == 'constructor':
            num_of_global_vars = self.symbol_table.count_variables_globally('field')
            self.VMwriter.write_push('constant', num_of_global_vars)
            self.VMwriter.write_call('Memory.alloc', 1)
            self.VMwriter.write_pop('pointer', 0)
        elif function_type[1] == 'method':
            self.VMwriter.write_push('argument', 0)
            self.VMwriter.write_pop('pointer', 0)
