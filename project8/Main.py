import os.path
import sys

from StackActionsTranslation import push_instruction, pop_instruction
from ArithmeticTranslation import arithmetic_logical_instruction, ARITHMETIC_OPS
from FunctionBranchingTranslation import (function_instruction, call_instruction, label, goto_instruction,
                                          conditional_goto_instruction, return_instruction)


def bootstrap() -> str:
    """Creates bootstrap instruction"""
    return '\n'.join([
        '/// BOOTSTRAP ///',
        '@256', 'D=A', '@SP', 'M=D',
        call_instruction('', 'Sys.init', 0, 'bootstrap'),
        '/// END BOOTSTRAP ///'
    ])


class Translator:
    def __init__(self, input_file: str, output_file, jump_counter=0, return_counter=0):
        self.input_file = input_file
        self.output_file = output_file
        self.name = os.path.basename(input_file)[:-3]
        self.jump_counter = jump_counter
        self.return_counter = return_counter
        self.current_function = ''

    def translate(self, instruction: str) -> str:
        """Receives a cleaned instruction and returns it's equivalent in HACK language"""
        try:
            args = instruction.split(' ')
            if args[0] == 'push':
                return push_instruction(args[1], args[2], self.name)
            elif args[0] == 'pop':
                return pop_instruction(args[1], args[2], self.name)
            elif args[0] in ARITHMETIC_OPS:
                if args[0] in ['eq', 'gt', 'lt']:
                    self.jump_counter += 1
                return arithmetic_logical_instruction(args[0], self.jump_counter)
            elif args[0] == 'label':
                return label(args[1], self.current_function)
            elif args[0] == 'goto':
                return goto_instruction(args[1], self.current_function)
            elif args[0] == 'if-goto':
                return conditional_goto_instruction(args[1], self.current_function)
            elif args[0] == 'call':
                temp = call_instruction(caller=self.current_function, called_func=args[1],
                                        args=int(args[2]), return_tag=self.return_counter)
                self.return_counter += 1
                return temp
            elif args[0] == 'function':
                self.current_function = args[1]
                return function_instruction(self.current_function, int(args[2]))
            elif args[0] == 'return':
                return return_instruction()
        except Exception as e:
            print(f'ERROR: Failed to translate {instruction}')
            sys.exit(1)

    def write(self):
        with open(self.input_file, 'r') as infile, open(self.output_file, 'a') as outfile:
            for line in infile:
                clean_line = line.split('//')[0]
                clean_line = clean_line.strip()
                if clean_line:
                    translated_line = self.translate(clean_line)
                    outfile.write(translated_line)

    def write_bootstrap(self):
        with(open(self.output_file, 'w')) as outfile:
            outfile.write(bootstrap())


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: VMtranslator <path/to/dir | file.vm>")
        sys.exit()
    path = sys.argv[1].rstrip('/')
    path = path.rstrip('\\')

    if os.path.isfile(path):
        if path.endswith('.vm'):
            output_file = path[:-3] + '.asm'
            print('Translating ' + path)
            translator = Translator(path, output_file)
            translator.write()
            print(f'Done! translated file at {path[:-2]+'asm'}')
        else:
            print('ERROR: wrong file format. expected file.vm')

    elif os.path.isdir(path):
        output_file = os.path.join(path, os.path.basename(path) + '.asm')
        print(output_file)
        translator = Translator('', output_file)
        for file in os.listdir(path):
            if file.endswith('.vm'):
                print(f'Translating {file}')
                translator.input_file = os.path.join(path, file)
                translator.write()
        print(f'Done! translated file at {output_file}')

    else:
        print('ERROR: Invalid path')
