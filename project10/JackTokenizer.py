from CONSTANTS import *


class JackTokenizer:
    def __init__(self, file):
        with open(file, 'r') as f:
            self.lines = f.read()
        self.clean_code()
        self.currToken = ''
        self.tokens = self.tokenize()
        self.tokens = self.replace_symbols()

    def clean_code(self):
        """ Removes comments from the file"""
        index = 0
        clean_text = ''
        while index < len(self.lines):  # Iterate over the entire text and clean the code
            current_char = self.lines[index]
            # In String
            if current_char == '\"':
                end_index = self.lines.find('\"', index + 1)
                clean_text += self.lines[index: end_index + 1]
                index = end_index + 1
            # Comment
            elif current_char == '/':
                # single line comment '//'
                if self.lines[index + 1] == '/':
                    end_index = self.lines.find('\n', index + 1)
                    index = end_index + 1
                    clean_text += ' '
                # multi line comment
                elif self.lines[index + 1] == '*':
                    end_index = self.lines.find('*/', index + 1)
                    index = end_index + 2
                    clean_text += ' '
                # / for divide
                else:
                    clean_text += self.lines[index]
                    index = index + 1
            else:
                clean_text += self.lines[index]
                index = index + 1

        # sets lines to the cleaned version
        self.lines = clean_text
        return

    def tokenize(self):
        """ Tokenizes the text"""
        return [self.token_type(word) for word in self.split_into_tokens(self.lines)]

    def replace_symbols(self):
        """
        Replaces symbols to avoid xml problems using the following guide:
        '<' : &lt
        '>' : &gt
        '"' : &quot
        '&' : &amp
        """
        return [self.replace_symbol(pair) for pair in self.tokens]

    def has_more_tokens(self):
        """ Checks if there are more tokens to process"""
        return self.tokens != []

    def peek(self):
        """ Returns the first token in tokens"""
        if self.has_more_tokens():
            return self.tokens[0]
        return 'ERROR', 'END OF FILE'

    def advance(self):
        """ Should only be called if hasMoreTokens() is true"""
        if self.has_more_tokens():
            self.currToken = self.tokens.pop(0)
            return self.currToken
        return 'ERROR', 'END OF FILE'

    @staticmethod
    def token_type(word):
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
    def split_into_tokens(text):
        """Breaks a single string into a list of tokens"""
        return WORD.findall(text)

    @staticmethod
    def replace_symbol(pair):
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
