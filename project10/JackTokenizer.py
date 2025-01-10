import re  # regular expression

KEYWORDS = {"class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean",
            "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"}
SYMBOLS = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '<', '>', '=', '~'}

# REGEX:
KEYWORD_REGEX = '(?!\\w)|'.join(KEYWORDS) + '(?!\\w)'
SYMBOLS_REGEX = '[' + re.escape('|'.join(SYMBOLS)) + ']'
INTEGER_REGEX = r'\d+'
STRINGS_REGEX = r'"[^"\n]*"'
IDENTIFIERS_REGEX = r'[\w]+'
WORD = re.compile(
    f'{KEYWORD_REGEX}|{SYMBOLS_REGEX}|{INTEGER_REGEX}|{STRINGS_REGEX}|{IDENTIFIERS_REGEX}')


class JackTokenizer:
    def __init__(self, file):
        with open(file, 'r') as f:
            self.lines = f.read()
        self.cleanCode()
        self.currToken = ''
        self.tokens = self.tokenize()
        self.tokens = self.replaceSymbols()

    def cleanCode(self):
        """ Removes comments from the file"""
        index = 0
        cleanText = ''
        while index < len(self.lines):  # Iterate over the entire text and clean the code
            currentChar = self.lines[index]
            # In String
            if currentChar == '\"':
                endIndex = self.lines.find('\"', index + 1)
                cleanText += self.lines[index: endIndex + 1]
                index = endIndex + 1
            # Comment
            elif currentChar == '/':
                # single line comment '//'
                if self.lines[index + 1] == '/':
                    endIndex = self.lines.find('\n', index + 1)
                    index = endIndex + 1
                    cleanText += ' '
                # multi line comment
                elif self.lines[index + 1] == '*':
                    endIndex = self.lines.find('*/', index + 1)
                    index = endIndex + 2
                    cleanText += ' '
                # / for divide
                else:
                    cleanText += self.lines[index]
                    index = index + 1
            else:
                cleanText += self.lines[index]
                index = index + 1

        # sets lines to the cleaned version
        self.lines = cleanText
        return

    @staticmethod
    def token(word):
        if re.match(KEYWORD_REGEX, word) is not None:
            return "keyword", word
        elif re.match(SYMBOLS_REGEX, word) is not None:
            return "symbol", word
        elif re.match(INTEGER_REGEX, word) is not None:
            return "integerConstant", word
        elif re.match(STRINGS_REGEX, word) is not None:
            return "stringConstant", word[1:-1]
        else:
            return "identifier", word

    @staticmethod
    def splitTokens(text):
        """Breaks a single string into a list of tokens"""
        return WORD.findall(text)

    @staticmethod
    def replaceSymbol(pair):
        """Replaces symbols with corresponding alternative representation"""
        token, val = pair
        if val == '<':
            return token, '&lt;'
        elif val == '>':
            return token, '&gt;'
        elif val == '"':
            return token, '&quot;'
        elif val == '&':
            return token, '&amp;'
        else:
            return token, val

    def tokenize(self):
        """ Tokenizes the text"""
        return [self.token(word) for word in self.splitTokens(self.lines)]

    def replaceSymbols(self):
        """
        Replaces symbols to avoid xml problems using the following guide:
        '<' : &lt
        '>' : &gt
        '"' : &quot
        '&' : &amp
        """
        return [self.replaceSymbol(pair) for pair in self.tokens]

    def hasMoreTokens(self):
        """ Checks if there are more tokens to process"""
        return self.tokens != []

    def peek(self):
        """ Returns the first token in tokens"""
        if self.hasMoreTokens():
            return self.tokens[0]
        return 'ERROR', 0

    def getToken(self):
        return self.tokens[0]

    def getValue(self):
        return self.currToken[1]

    def advance(self):
        """ Should only be called if hasMoreTokens() is true"""
        self.currToken = self.tokens.pop(0)
        return self.currToken
