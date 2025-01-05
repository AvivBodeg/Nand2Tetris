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
        self.func_name = ''
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

    def translate_label(self, command: str) -> list:
        """Returns a hack assembly label"""
        label = command.split(' ')[1]
        return [f'({self.func_name}${label})']

    def translate_goto(self, command: str) -> list:
        """Returns a hack assembly unconditional goto command"""
        label = command.split(' ')[1]
        return [f'@{self.func_name}${label}', '0;JMP']

    def translate_if_goto(self, command: str) -> list:
        """Returns a hack assembly if-goto command"""
        label = command.split(' ')[1]
        return ['@SP', 'AM=M-1', 'D=M', f'@{self.func_name}${label}', 'D;JNE']

    def translate_function(self, command: str) -> list:
        """Returns a hack assembly function command"""
        args = command.split(' ')  # args = [function, func_name, variablesNum]
        self.func_name = args[1]
        output = [f'({self.func_name})']
        for _ in range(int(args[2])):
            output.extend(self.translate_push('push constant 0'))
        return output

    def translate_call(self, command: str) -> list:
        """Returns a hack assembly code that cals a function"""
        args = command.split(' ')
        return_label = f'{self.func_name}$ret.{self.label_counter}'
        self.label_counter += 1
        output = [f'@{return_label}', 'D=A', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
        # push local, arguments this and that into stack
        for segment in ['LCL', 'ARG', 'THIS', 'THAT']:
            output.extend([f'@{segment}', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1'])
        # argument = SP-5-num_args
        output.extend(['@SP', 'D=M', '@5', 'D=D-A', f'@{args[2]}', 'D=D-A', '@ARG', 'M=D'])
        # local = sp, goto func_name and (return_label)
        output.extend(['@SP', 'D=M', '@LCL', 'M=D', f'@{args[1]}', '0;JMP', f'({return_label})'])
        return output

    @staticmethod
    def translate_return() -> list:
        """Returns a hack assembly code to return from a function"""
        output = [
            '@LCL', 'D=M', '@R13', 'M=D',  # Store LCL in R13
            '@5', 'A=D-A', 'D=M', '@R14', 'M=D',  # Store (end_frame -5) in R14
            '@SP', 'AM=M-1', 'D=M', '@ARG', 'A=M', 'M=D',  # ARG = pop()
            '@ARG', 'D=M+1', '@SP', 'M=D'
        ]
        # restore stored segments
        for segment in ['THAT', 'THIS', 'ARG', 'LCL']:
            output.extend(['@R13', 'AM=M-1', 'D=M', f'@{segment}', 'M=D'])
        output.extend(['@R14', 'A=M', '0;JMP'])
        return output
