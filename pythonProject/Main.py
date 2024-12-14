import os
import sys
from CodeTranslator import CodeTranslator


class VMTranslator:
    def __init__(self, input_file: str, output_file: str):
        self.input_file = input_file
        self.output_file = output_file
        self.translator = CodeTranslator(os.path.basename(input_file))
        if os.path.exists(self.output_file):
            #  Reset the file if it exists by deleting and recreating it
            print(f'Overwriting {self.output_file}')
            os.remove(self.output_file)

    def multi_file_init(self):
        """in case of a multi-file program, initialize the file with OS and Sys.init"""
        with open(self.output_file, 'w') as outfile:
            commands = self.translator.translate_function('function OS 0')
            commands.extend(self.translator.translate_call('call Sys.init 0'))
            for command in commands:
                outfile.write(command + '\n')

    def translate(self, command: str):

        args = command.split(' ')
        if args[0] in ['add', 'sub', 'and', 'or']:
            return self.translator.translate_arithmetic(command)
        elif args[0] in ['eq', 'gt', 'lt']:
            return self.translator.translate_comparison(command)
        elif args[0] in ['neg', 'not']:
            return self.translator.translate_negation(command)

        match args[0]:
            case 'push':
                return self.translator.translate_push(command)
            case 'pop':
                return self.translator.translate_pop(command)
            case 'label':
                return self.translator.translate_label(command)
            case 'goto':
                return self.translator.translate_goto(command)
            case 'if-goto':
                return self.translator.translate_if_goto(command)
            case 'function':
                return self.translator.translate_function(command)
            case 'call':
                return self.translator.translate_call(command)
            case 'return':
                return self.translator.translate_return()
            case _:
                raise Exception('Unknown command')

    def write(self, in_file: str):
        self.translator.set_file_name(os.path.basename(in_file))
        with open(in_file, 'r') as infile, open(self.output_file, 'a') as outfile:
            for line in infile:
                cleaned_line = line.split('//')[0]
                cleaned_line = cleaned_line.strip()
                if cleaned_line:
                    translated_line = '\n'.join(self.translate(cleaned_line))
                    outfile.write(translated_line)
                    outfile.write('\n')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: VMTranslator <path/to/dir | file.vm>')
        sys.exit(1)
    output_file = ''
    path = sys.argv[1]
    if os.path.isdir(path):
        temp = path.strip('/').strip('\\')
        output_file = os.path.join(path, os.path.basename(temp) + '.asm')
        vm = VMTranslator(path, output_file)

        # Test Fix for Multi-file program
        file_count = 0
        for file in os.listdir(path):
            if file.endswith('.vm'):
                file_count += 1
            if file_count == 2:
                vm.multi_file_init()
                break

        for file in os.listdir(path):
            if file.endswith('.vm'):
                print(f'Processing {file}')
                vm.write(os.path.join(path, file))

    elif os.path.isfile(path):
        if path.endswith('.vm'):
            output_file = path[:-2] + 'asm'
            vm = VMTranslator(path, output_file)
            vm.write(path)
        else:
            print('ERROR: expect file.vm')
            sys.exit(1)

    print(f'Done! translated file at {output_file}')