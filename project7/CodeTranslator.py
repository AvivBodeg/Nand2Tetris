from symtable import SymbolTable

SYMBOL_TABLE = {
    # Arithmetic Operators
    'add': 'M=D+M',
    'sub': 'M=M-D',
    'and': 'M=D&M',
    'or': 'M=D|M',
    'neg': 'M=-M',
    'not': 'M=!M',
    'eq': 'D;JEQ',
    'gt': 'D;JGT',
    'lt': 'D;JLT',
    # Assembly Symbols
    'local': '@LCL',
    'argument': '@ARG',
    'this': '@THIS',
    'that': '@THAT',
    'constant': '',
    'static': '',
    'pointer': '@3',
    'temp': '@5'
}

class CodeTranslator:
    def __init__(self, file: str):
        self.file_name = file
        self.label_counter = 0

    def set_file_name(self, file_name: str):
        self.file_name = file_name

    @staticmethod
    def translate_arithmetic(command: str) -> list:
        """Returns a hack assembly command that does the arithmetic operation provided"""
        args = command.split(' ')
        return ['@SP', 'AM=M-1', 'D=M', '@SP', 'A=M-1', SYMBOL_TABLE[args[0]]]

    @staticmethod
    def translate_negation(command: str) -> list:
        """Returns a hack assembly command that does the negation provided"""
        args = command.split(' ')
        return ['@SP', 'A=M-1', SYMBOL_TABLE[args[0]]]

    def translate_comparison(self, command: str) -> list:
        """Returns a hack assembly command that does the comparison provided"""
        args = command.split(' ')
        label = f'Label{self.label_counter}'
        self.label_counter += 1
        return ['@SP', 'AM=M-1', 'D=M', '@SP', 'A=M-1', 'D=M-D', 'M=-1',
                  f'@{label}', SYMBOL_TABLE[args[0]], '@SP', 'A=M-1', 'M=0', f'({label})']

    def translate_push(self, command: str) -> list:
        """Returns a hack assembly command that craetes a push to the provided segment"""
        args = command.split(' ')
        if args[1] == 'constant':
            return [f'@{args[2]}', 'D=A', '@SP', 'AM=M+1', 'A=A-1', 'M=D']
        elif args[1] == 'static':
            return [f'@{self.file_name[:-3]}.{args[2]}', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
        elif args[1] in ['local', 'argument', 'this', 'that', 'constant', 'temp', 'pointer']:
            output = [f'@{args[2]}', 'D=A', SYMBOL_TABLE[args[1]]]
            if args[1] != 'pointer' and args[1] != 'temp':
                output.append('A=M')
            output.extend(['A=D+A', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1'])
            return output
        else:
            raise Exception(f'Unknown command: {command}')

    def translate_pop(self, command: str) -> list:
        """Returns a hack assembly command that creates a pop from the provided segment"""
        args = command.split(' ')
        if args[1] == 'static':
            return ['@SP', 'AM=M-1', 'D=M', f'@{self.file_name[:-3]}.{args[2]}', 'M=D']
        elif args[1] in ['local', 'argument', 'this', 'that', 'temp', 'pointer']:
            output = [f'@{args[2]}', 'D=A', SYMBOL_TABLE[args[1]]]
            if args[1] != 'pointer' and args[1] != 'temp':
                output.append('A=M')
            output.extend(['D=D+A', '@R13', 'M=D', '@SP', 'AM=M-1', 'D=M', '@R13', 'A=M', 'M=D'])
            return output
        elif args[1] == 'constant':
            raise Exception('Can\'t pop from constant')
        else:
            raise Exception(f'Unknown command: {command}')
