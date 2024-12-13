import os.path
import sys

from POP_PUSH_Translation import push_instruction, pop_instruction
from Arithmetic_Translation import arithmetic_logical_instruction, ARITHMETIC_OPS


class Translator:
    def __init__(self, input_file: str, output_file, jump_counter=0):
        self.input_file = input_file
        self.output_file = output_file
        self.name = os.path.basename(input_file)[:-3]
        self.jump_counter = jump_counter

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
        except Exception as e:
            print(f'ERROR: Failed to translate {instruction}')
            sys.exit(1)

    def write(self, append: bool):
        action = 'a' if append else 'w'
        with open(self.input_file, 'r') as infile, open(self.output_file, action) as outfile:
            for line in infile:
                clean_line = line.split('//')[0]
                clean_line = clean_line.strip()
                if clean_line:
                    translated_line = self.translate(clean_line)
                    outfile.write(translated_line)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: VMtranslator <path/to/dir | file.vm>")
        sys.exit()
    path = sys.argv[1]

    if os.path.isfile(path):
        if path.endswith('.vm'):
            output_file = path[:-3] + '.asm'
            print('Translating ' + path)
            translator = Translator(path, output_file)
            translator.write(False)
            print(f'Done! translated file at {path[:-2]+'asm'}')
        else:
            print('ERROR: wrong file format. expected file.vm')

    elif os.path.isdir(path):
        output_file = os.path.join(path, os.path.basename(path) + '.asm')
        print(output_file)
        for file in os.listdir(path):
            if file.endswith('.vm'):
                print(f'Translating {file}')
                translator = Translator(os.path.join(path, file), output_file)
                translator.write(True)
        print(f'Done! translated file at {output_file}')

    else:
        print('ERROR: Invalid path')
