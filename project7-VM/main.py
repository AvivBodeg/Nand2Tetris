import os
import sys
from CodeWriter import CodeWriter
from Parser import Parser


# noinspection DuplicatedCode
class VM:
    def __init__(self, file_name):
        self.input_file = file_name
        self.output_file = self.input_file[:-2] + 'asm'
        self.parser = Parser(self.input_file)
        self.commands = self.parser.commands
        self.codeWriter = CodeWriter(self.input_file)

    def write_file(self):
        file = open(self.output_file, 'w')
        for command in self.commands:
            c_type = self.parser.command_type(command)
            block = []
            if c_type == "C_ARITHMETIC":
                block = self.codeWriter.write_arithmetic(command)
            elif c_type == "C_POP" or c_type == "C_PUSH":
                segment = self.parser.get_argument1(command)
                index = self.parser.get_argument2(command)
                block = self.codeWriter.write_pop_push(c_type, segment, index)
            instructions = "\n".join(block)
            file.write(instructions)
        file.close()

    def write_dir(self, file_name):
        file = open(file_name, 'a')
        for command in self.commands:
            c_type = self.parser.command_type(command)
            block = []
            if c_type == "C_ARITHMETIC":
                block = self.codeWriter.write_arithmetic(command)
            elif c_type == "C_POP" or c_type == "C_PUSH":
                segment = self.parser.get_argument1(command)
                index = self.parser.get_argument2(command)
                block = self.codeWriter.write_pop_push(c_type, segment, index)
            instructions = "\n".join(block)
            file.write(instructions)
        file.write('\n')
        file.close()


def main():
    if len(sys.argv) != 2:
        print("Usage: VMtranslator <path/to/dir | file.vm>")
        sys.exit()

    path = sys.argv[1]

    if os.path.isfile(path):
        if path.endswith('.vm'):
            vm = VM(sys.argv[1])
            vm.write_file()
        else:
            print("ERROR: wrong file type. expected file.vm")
    elif os.path.isdir(path):
        path = path[:-1] if path.endswith("/") or path.endswith("\\") else path
        name = os.path.basename(path) + '.asm'
        name = os.path.join(path, name)

        # reset file if exists
        f = open(name, 'w')
        f.close()

        for file in os.listdir(path):
            if file.endswith(".vm"):
                vm = VM(os.path.join(path, file))
                vm.write_dir(name)
    else:
        print("ERROR: Invalid path")


if __name__ == '__main__':
    main()
