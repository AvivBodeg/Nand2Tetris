from JackTokenizer import JackTokenizer

UNARY_OPERATORS = {'-', '~'}
BINARY_OPERATORS = {'+', '-', '*', '/', '|', '=', '&lt;', '&gt;', '&amp;'}
KEYWORD_CONSTANTS = {'true', 'false', 'null', 'this'}


class CompilationEngine:
    def __init__(self, inFile, outFile):
        self.tokenizer = JackTokenizer(inFile)
        self.rules = []
        self.outputFile = outFile
        self.indent = ''

    def incIndent(self):
        self.indent += '  '

    def decIndent(self):
        if len(self.indent) > 1:
            self.indent = self.indent[:-2]

    def advance(self):
        token, value = self.tokenizer.advance()
        self.writeTerminal(token, value)

    def writeNonTerminalStart(self, rule):
        with open(self.outputFile, 'a') as outFile:
            outFile.write(f'{self.indent}<{rule}>\n')
        self.rules.append(rule)
        self.incIndent()

    def writeNonTerminalEnd(self):
        self.decIndent()
        rule = self.rules.pop()
        with open(self.outputFile, 'a') as outFile:
            outFile.write(f'{self.indent}</{rule}>\n')

    def writeTerminal(self, token, value):
        with open(self.outputFile, 'a') as outFile:
            outFile.write(f'{self.indent}<{token}> {value} </{token}>\n')

    def isValInList(self, lst):
        """ checks if the next value is in the list"""
        token, val = self.tokenizer.peek()
        return val in lst

    def isNextVal(self, value):
        """ checks if the next value is the one supplied"""
        token, val = self.tokenizer.peek()
        return val == value

    def isNextToken(self, token):
        """ checks if the next token is the one supplied"""
        toke, val = self.tokenizer.peek()
        return toke == token

    def hasClassVariables(self):
        """ checks if the class has a field/static declaration"""
        return self.isNextVal('static') or self.isNextVal('field')

    def hasSubroutine(self):
        return self.isNextVal('constructor') or self.isNextVal('method') or self.isNextVal('function')

    def compileClass(self):
        """ Compiles a class"""
        self.writeNonTerminalStart('class')
        self.advance()  # class keyword
        self.advance()  # class name
        self.advance()  # '{'
        if self.hasClassVariables():
            self.compileClassVariables()
        while self.hasSubroutine():
            self.compileSubroutine()
        self.advance()  # '}'
        self.writeNonTerminalEnd()

    def compileSubroutine(self):
        """ compiles a method/function/constructor"""
        self.writeNonTerminalStart('subroutineDec')
        self.advance()  # method/function/constructor
        self.advance()  # return tpe
        self.advance()  # name/new
        self.advance()  # '{'
        self.compileParameterList()
        self.advance()  # '}'
        self.compileSubroutineBody()
        self.writeNonTerminalEnd()

    def compileClassVariables(self):
        """ Compiles the static and field declarations"""
        while self.hasClassVariables():
            self.writeNonTerminalStart('classVarDec')
            self.writeClassVarDec()
            self.writeNonTerminalEnd()

    def writeClassVarDec(self):
        """ writes a class variable in the form of <static|field> <type> var_name* """
        self.advance()  # static/field
        self.advance()  # type
        self.advance()  # var_name
        while self.isNextVal(','):
            self.advance()  # ','
            self.advance()  # var_name
        self.advance()  # ';'

    def compileParameterList(self):
        """ compiles a list of parameters, possibly empty"""
        self.writeNonTerminalStart('parameterList')
        while self.hasParameter():
            self.writeParameter()
        self.writeNonTerminalEnd()

    def hasParameter(self):
        return not self.isNextToken('symbol')

    def writeParameter(self):
        self.advance()  # type
        self.advance()  # param_name
        if self.isNextVal(','):
            self.advance()  # ','

    def compileSubroutineBody(self):
        self.writeNonTerminalStart('subroutineBody')
        self.advance()  # '{'
        while self.hasValDec():
            self.compileVarDec()
        self.compileStatements()
        self.advance()  # '}'
        self.writeNonTerminalEnd()

    def hasValDec(self):
        return self.isNextVal('var')

    def compileVarDec(self):
        """" compiles a variable declaration"""
        self.writeNonTerminalStart('varDec')
        self.advance()  # 'var'
        self.advance()  # type
        self.advance()  # var_name
        while self.isNextVal(','):
            self.advance()  # ','
            self.advance()  # var_name
        self.advance()  # ';'
        self.writeNonTerminalEnd()

    def compileStatements(self):
        """ compiles a list of statements"""
        self.writeNonTerminalStart('statements')
        while self.hasStatement():
            if self.isNextVal("do"):
                self.compileDo()
            elif self.isNextVal("while"):
                self.compileWhile()
            elif self.isNextVal("return"):
                self.compileReturn()
            elif self.isNextVal("let"):
                self.compileLet()
            elif self.isNextVal("if"):
                self.compileIf()
        self.writeNonTerminalEnd()

    def hasStatement(self):
        return (self.isNextVal('do')
                or self.isNextVal('if')
                or self.isNextVal('while')
                or self.isNextVal('let')
                or self.isNextVal('return')
                )

    def compileDo(self):
        """ compiles do statement"""
        self.writeNonTerminalStart('doStatement')
        self.advance()  # do
        self.compileSubroutineCall()
        self.advance()  # ';'
        self.writeNonTerminalEnd()

    def compileSubroutineCall(self):
        """ compiles subroutine call. do name([list])"""
        self.advance()  # name
        if self.isNextVal('.'):
            self.advance()  # '.'
            self.advance()  # subroutine name
        self.advance()  # '('
        self.compileExpressionList()
        self.advance()  # ')'

    def compileExpressionList(self):
        """compiles a list of experssion, possibly empty"""
        self.writeNonTerminalStart('expressionList')
        if self.termExists():
            self.compileExpression()
        while self.isNextVal(','):
            self.advance()  # ','
            self.compileExpression()
        self.writeNonTerminalEnd()

    def termExists(self):
        return (self.isNextToken('integerConstant')
                or self.isNextToken('stringConstant')
                or self.isNextToken('identifier')
                or self.isValInList(UNARY_OPERATORS)
                or self.isValInList(KEYWORD_CONSTANTS)
                or self.isNextVal('('))

    def compileExpression(self):
        self.writeNonTerminalStart('expression')
        self.compileTerm()
        while self.isValInList(BINARY_OPERATORS):
            self.advance()  # op_symbol
            self.compileTerm()
        self.writeNonTerminalEnd()

    def compileTerm(self):
        """ compiles term"""
        self.writeNonTerminalStart('term')

        if (self.isNextToken('integerConstant')
                or self.isNextToken('stringConstant')
                or self.isValInList(KEYWORD_CONSTANTS)):
            self.advance()  # constant
        elif self.isNextToken('identifier'):
            self.advance()  # name
            if self.isNextVal('['):
                self.writeArrayIndex()
            if self.isNextVal('('):
                self.advance()  # '('
                self.compileExpressionList()
                self.advance()  # ')'
            if self.isNextVal('.'):
                self.advance()  # '.'
                self.advance()  # subroutine_name
                self.advance()  # '('
                self.compileExpressionList()
                self.advance()  # ')'
        elif self.isValInList(UNARY_OPERATORS):
            self.advance()  # op
            self.compileTerm()
        elif self.isNextVal('('):
            self.advance()  # '('
            self.compileExpression()
            self.advance()  # ')'
        self.writeNonTerminalEnd()

    def compileLet(self):
        """ compiles let statement"""
        self.writeNonTerminalStart('letStatement')
        self.advance()  # let
        self.advance()  # var_name
        if self.isNextVal('['):  # array
            self.writeArrayIndex()
        self.advance()  # '='
        self.compileExpression()
        self.advance()  # ';'
        self.writeNonTerminalEnd()

    def compileIf(self):
        """ compiles if statement"""
        self.writeNonTerminalStart('ifStatement')
        self.advance()  # if
        self.advance()  # '('
        self.compileExpression()
        self.advance()  # ')'
        self.advance()  # '{'
        self.compileStatements()
        self.advance()  # '}'
        if self.isNextVal('else'):
            self.advance()  # else
            self.advance()  # '{'
            self.compileStatements()
            self.advance()  # '}'
        self.writeNonTerminalEnd()

    def compileWhile(self):
        """ compiles while statement"""
        self.writeNonTerminalStart('whileStatement')
        self.advance()  # while
        self.advance()  # '('
        self.compileExpression()
        self.advance()  # ')'
        self.advance()  # '{'
        self.compileStatements()
        self.advance()  # '}'
        self.writeNonTerminalEnd()

    def compileReturn(self):
        self.writeNonTerminalStart('returnStatement')
        self.advance()  # return
        while self.termExists():
            self.compileExpression()
        self.advance()  # ';'
        self.writeNonTerminalEnd()

    def writeArrayIndex(self):
        self.advance()  # '['
        self.compileExpression()
        self.advance()  # ']'
