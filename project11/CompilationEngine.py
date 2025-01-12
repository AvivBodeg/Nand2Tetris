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
            self.write_class_var_dec()  # TODO: writers

    def compile_parameter_list(self, function_type):
        """ compiles a list of parameters, possibly empty"""
        if function_type[1] == 'method':
            self.symbol_table.define('this', 'self', 'arg')
        while self.has_parameter():
            self.write_parameter()  # TODO: writes

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


    # TODO: ########################## here
    def compile_term(self):
        """ compiles term"""
        self.write_non_terminal_start('term')
        if (self.is_next_token('integerConstant')
                or self.is_next_token('stringConstant')
                or self.is_next_val_in_list(KEYWORD_CONSTANTS)):
            self.advance()  # constant
        elif self.is_next_token('identifier'):
            self.advance()  # name
            if self.is_next_val('['):
                self.write_array_index()
            if self.is_next_val('('):
                self.advance()  # '('
                self.compile_expression_list()
                self.advance()  # ')'
            if self.is_next_val('.'):
                self.advance()  # '.'
                self.advance()  # subroutine_name
                self.advance()  # '('
                self.compile_expression_list()
                self.advance()  # ')'
        elif self.is_next_val_in_list(UNARY_OPERATORS):
            self.advance()  # op
            self.compile_term()
        elif self.is_next_val('('):
            self.advance()  # '('
            self.compile_expression()
            self.advance()  # ')'
        self.write_non_terminal_end()

    def compile_statements(self):
        """ compiles a list of statements"""
        self.write_non_terminal_start('statements')
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
        self.write_non_terminal_end()
    
    #TODO: add all the rest of the compiles

    # WRITES TODO: all of them
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

    def write_pop(self, name):
        pass

    def write_push(self, name, sub_name):
        pass

    def load_pointer(self, function_type):
        pass
