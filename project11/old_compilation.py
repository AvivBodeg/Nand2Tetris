from JackTokenizer import JackTokenizer
from CONSTANTS import UNARY_OPERATORS, BINARY_OPERATORS, KEYWORD_CONSTANTS

class CompilationEngine:
    def __init__(self, in_file, out_file):
        self.tokenizer = JackTokenizer(in_file)
        self.rules = []
        self.output_file = out_file
        self.indent = ''

    def inc_indent(self):
        """ increases indent by two spaces"""
        self.indent += '  '

    def dec_indent(self):
        """ decreases indent by two spaces if possible"""
        if len(self.indent) > 1:
            self.indent = self.indent[:-2]

    def advance(self):
        """ gets and writes the next token"""
        token, value = self.tokenizer.advance()
        self.write_terminal(token, value)

    # WRITES TO FILE:
    def write_non_terminal_start(self, rule):
        """ wirtes <rule> and adds it to rules"""
        with open(self.output_file, 'a') as outFile:
            outFile.write(f'{self.indent}<{rule}>\n')
        self.rules.append(rule)
        self.inc_indent()

    def write_non_terminal_end(self):
        """ writes </rule> using the last rule in the list that hasn't been closed"""
        self.dec_indent()
        rule = self.rules.pop()
        with open(self.output_file, 'a') as outFile:
            outFile.write(f'{self.indent}</{rule}>\n')

    def write_terminal(self, token, value):
        """ writes <token> value </token>"""
        with open(self.output_file, 'a') as outFile:
            outFile.write(f'{self.indent}<{token}> {value} </{token}>\n')

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

    # CHECKERS:
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

    # COMPILERS:
    def compile_class(self):
        """ Compiles a class"""
        self.write_non_terminal_start('class')
        self.advance()  # class keyword
        self.advance()  # class name
        self.advance()  # '{'
        if self.has_class_variables():
            self.compile_class_variables()
        while self.has_subroutine():
            self.compile_subroutine()
        self.advance()  # '}'
        self.write_non_terminal_end()

    def compile_subroutine(self):
        """ compiles a method/function/constructor"""
        self.write_non_terminal_start('subroutineDec')
        self.advance()  # method/function/constructor
        self.advance()  # return tpe
        self.advance()  # name/new
        self.advance()  # '{'
        self.compile_parameter_list()
        self.advance()  # '}'
        self.compile_subroutine_body()
        self.write_non_terminal_end()

    def compile_class_variables(self):
        """ Compiles the static and field declarations"""
        while self.has_class_variables():
            self.write_non_terminal_start('classVarDec')
            self.write_class_var_dec()
            self.write_non_terminal_end()

    def compile_parameter_list(self):
        """ compiles a list of parameters, possibly empty"""
        self.write_non_terminal_start('parameterList')
        while self.has_parameter():
            self.write_parameter()
        self.write_non_terminal_end()

    def compile_subroutine_body(self):
        self.write_non_terminal_start('subroutineBody')
        self.advance()  # '{'
        while self.has_val_dec():
            self.compile_var_dec()
        self.compile_statements()
        self.advance()  # '}'
        self.write_non_terminal_end()

    def compile_var_dec(self):
        """" compiles a variable declaration"""
        self.write_non_terminal_start('varDec')
        self.advance()  # 'var'
        self.advance()  # type
        self.advance()  # var_name
        while self.is_next_val(','):
            self.advance()  # ','
            self.advance()  # var_name
        self.advance()  # ';'
        self.write_non_terminal_end()

    def compile_subroutine_call(self):
        """ compiles subroutine call. do name([list])"""
        self.advance()  # name
        if self.is_next_val('.'):
            self.advance()  # '.'
            self.advance()  # subroutine name
        self.advance()  # '('
        self.compile_expression_list()
        self.advance()  # ')'

    def compile_expression_list(self):
        """compiles a list of experssion, possibly empty"""
        self.write_non_terminal_start('expressionList')
        if self.term_exists():
            self.compile_expression()
        while self.is_next_val(','):
            self.advance()  # ','
            self.compile_expression()
        self.write_non_terminal_end()

    def compile_expression(self):
        """ compiles an expression"""
        self.write_non_terminal_start('expression')
        self.compile_term()
        while self.is_next_val_in_list(BINARY_OPERATORS):
            self.advance()  # op_symbol
            self.compile_term()
        self.write_non_terminal_end()

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

    # STATEMENTS:
    def compile_let(self):
        """ compiles let statement"""
        self.write_non_terminal_start('letStatement')
        self.advance()  # let
        self.advance()  # var_name
        if self.is_next_val('['):  # array
            self.write_array_index()
        self.advance()  # '='
        self.compile_expression()
        self.advance()  # ';'
        self.write_non_terminal_end()

    def compile_if(self):
        """ compiles if statement"""
        self.write_non_terminal_start('ifStatement')
        self.advance()  # if
        self.advance()  # '('
        self.compile_expression()
        self.advance()  # ')'
        self.advance()  # '{'
        self.compile_statements()
        self.advance()  # '}'
        if self.is_next_val('else'):
            self.advance()  # else
            self.advance()  # '{'
            self.compile_statements()
            self.advance()  # '}'
        self.write_non_terminal_end()

    def compile_do(self):
        """ compiles do statement"""
        self.write_non_terminal_start('doStatement')
        self.advance()  # do
        self.compile_subroutine_call()
        self.advance()  # ';'
        self.write_non_terminal_end()

    def compile_while(self):
        """ compiles while statement"""
        self.write_non_terminal_start('whileStatement')
        self.advance()  # while
        self.advance()  # '('
        self.compile_expression()
        self.advance()  # ')'
        self.advance()  # '{'
        self.compile_statements()
        self.advance()  # '}'
        self.write_non_terminal_end()

    def compile_return(self):
        """ compiles return statement :)"""
        self.write_non_terminal_start('returnStatement')
        self.advance()  # return
        while self.term_exists():
            self.compile_expression()
        self.advance()  # ';'
        self.write_non_terminal_end()

    # HELPER WRITES:
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

    def write_parameter(self):
        """writes a single parameter, with option to add ',' if there are multiple"""
        self.advance()  # type
        self.advance()  # param_name
        if self.is_next_val(','):
            self.advance()  # ','