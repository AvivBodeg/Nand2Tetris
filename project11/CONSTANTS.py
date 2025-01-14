import re

UNARY_OPERATORS = {'-', '~'}
BINARY_OPERATORS = {'+', '-', '*', '/', '|', '=', '&lt;', '&gt;', '&amp;'}
KEYWORD_CONSTANTS = {'true', 'false', 'null', 'this'}

KEYWORDS = {"class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean",
            "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"}
SYMBOLS = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '<', '>', '=', '~'}

# REGEX:
KEYWORD_REGEX = r'(?!\w)|'.join(KEYWORDS) + r'(?!\w)'
SYMBOLS_REGEX = '[' + re.escape('|'.join(SYMBOLS)) + ']'
INTEGER_REGEX = r'\d+'
STRINGS_REGEX = r'"[^"\n]*"'
IDENTIFIERS_REGEX = r'[\w]+'
WORD = re.compile(
    f'{KEYWORD_REGEX}|{SYMBOLS_REGEX}|{INTEGER_REGEX}|{STRINGS_REGEX}|{IDENTIFIERS_REGEX}')

GLOBAL = 'global'

ARITHMETIC_OPERATORS = {'+': 'add', '-': 'sub', '|': 'or', '&': 'and', '=': 'eq', '<': 'lt', '>': 'gt'}

STATEMENTS = ['do', 'let', 'if', 'while', 'return']