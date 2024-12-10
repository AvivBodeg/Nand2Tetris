import os, sys
from Dictionaries import DEST_MAP, JUMP_MAP, COMP_MAP
from SymbolTable import SymbolTable


class Assembler:
    def __init__(self, input_file):
        self.input_file = input_file
        self.output_file = input_file[:-3] + "hack"
        self.instructions = []
        self.binary_instructions = []
        self.symbol_table = SymbolTable()
        self.next_variable_address = 16

    def parse_file(self):
        """Initializes @self.instructions list with cleand lines"""
        with open(self.input_file, 'r') as file_lines:
            for line in file_lines:
                cleaned_line = line.split('//')[0]  # remove comments
                cleaned_line = cleaned_line.strip()  # remove whitespaces
                if cleaned_line:  # line isn't empty after cleaning
                    self.instructions.append(cleaned_line)

    def first_pass(self):
        """Iterates over @instructions and records jump addresses"""
        current_address = 0
        for instruction in self.instructions:
            if instruction.startswith('(') and instruction.endswith(')'):
                label = instruction[1:-1]
                self.symbol_table.set_loop(label, current_address)
            else:
                current_address += 1

    def second_pass(self):
        """Translates @instructions into binary"""
        for instruction in self.instructions:
            if instruction.startswith('('):  # Label
                continue
            elif instruction.startswith('@'):  # A instruction
                self.binary_instructions.append(self.translate_a_instruction(instruction))
            else:  # C instruction
                self.binary_instructions.append(self.translate_c_instruction(instruction))

    def create_hack_file(self):
        instructions = "\n".join(self.binary_instructions)
        with open(self.output_file, 'w') as file:
            file.write(instructions)

    def translate_a_instruction(self, instruction: str) -> str:
        """Returns an A-instruction string compromised of 0 and the address of @instruction as a 15bit String"""
        symbol = instruction[1:]
        if symbol.isdigit():
            address = int(symbol)
        else:
            address = self.symbol_table.get_address(symbol)
        return format(address, '016b')

    @staticmethod
    def translate_c_instruction(instruction) -> str:
        """Returns a C-instruction made from 16bits according to the Table from the lecture"""
        prefix = '111'
        dest = '000'
        jump = '000'
        if '=' in instruction:
            split = instruction.split('=')
            dest = DEST_MAP[split[0]]
            instruction = split[1]
        if ';' in instruction:
            split = instruction.split(';')
            jump = JUMP_MAP[split[1]]
            instruction = split[0]
        return prefix + COMP_MAP[instruction] + dest + jump

    def assemble(self):
        self.parse_file()
        self.first_pass()
        self.second_pass()
        self.create_hack_file()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: Main.py <path/to/file.asm>')
        sys.exit()

    input_path = sys.argv[1]
    if os.path.isfile(input_path):
        if not input_path.endswith('.asm'):
            print('Invalid file type, expected .asm')
            sys.exit()
        else:
            print(f'Processing {input_path}...')
            assembler = Assembler(os.path.join(input_path))
            assembler.assemble()
            print('Completed assembling')
    else:
        print('Error: Expected a file path')
    # elif os.path.isdir(input_path):
    #     for file in os.listdir(input_path):
    #         if file.endswith('.asm'):
    #             print(f'Processing {file}...')
    #             assembler = Assembler(os.path.join(input_path, file))
    #             assembler.assemble()
    #     print('Completed assembling')
