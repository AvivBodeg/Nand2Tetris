import os


class CodeWriter:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_name = os.path.basename(self.file_path)[:-3]
        self.label_counter = 0  # to prevent reuses of labels
        self.symbols = {
            # Arithmetic Operators
            "add": "M=D+M",
            "sub": "M=M-D",
            "and": "M=D&M",
            "or": "M=D|M",
            "neg": "M=-M",
            "not": "M=!M",
            "eq": "D;JEQ",
            "gt": "D;JGT",
            "lt": "D;JLT",
            # Assembly Symbols
            "local": "@LCL",
            "argument": "@ARG",
            "this": "@THIS",
            "that": "@THAT",
            "constant": "",
            "static": "",
            "pointer": "@3",
            "temp": "@5"
        }

    @staticmethod
    def comment(command: str):
        """Returns a comment to write before a block"""
        return f"// Command {command}\n"

    def write_arithmetic(self, command: str) -> list:
        if command in ["add", "sub", "and", "or"]:
            return self.write_basic_arithmetic(command)
        elif command in ["eq", "gt", "lt"]:
            return self.write_compare_arithmetic(command)
        elif command in ["neg", "not"]:
            return self.write_compare_neg_not(command)
        else:
            raise NameError("Unexpected Arithmetic Command")

    def write_basic_arithmetic(self, command: str) -> list:
        """command is either 'add', 'sub', 'and' or 'or''"""
        output = []
        # pop Stack into D:
        output.append("@SP")
        output.append("AM=M-1")
        output.append("D=M")
        # access to Stack[-1]:
        output.append("@SP")
        output.append("A=M-1")
        output.append(self.symbols[command])  # use the Arithmetic Operator

        output.append(" ")  # empty line for easier reading
        return output

    def write_compare_arithmetic(self, command:str) -> list:
        """command is either 'eq', 'gt', 'lt''"""
        output = []
        jump_label = "CompLabel" + str(self.label_counter)
        self.label_counter += 1
        # pop Stack into D
        output.append("@SP")
        output.append("AM=M-1")
        output.append("D=M")
        # access to Stack[-1]:
        output.append("@SP")
        output.append("A=M-1")
        # calculate the difference
        output.append("D=M-D")
        # set the Stack to True:
        output.append("M=-1")
        # load the jump label into A.
        output.append("@" + jump_label)
        # if the statement is True: jump, else update the Stack to False:
        output.append(self.symbols[command])
        # set the Stack[-1] to False
        output.append("@SP")
        output.append("A=M-1")
        output.append("M=0")
        output.append("(" + jump_label + ")")  # jump_label for True state

        output.append(" ")  # empty line for easier reading
        return output

    def write_compare_neg_not(self, command: str) -> list:
        """command is either 'neg' or 'not' """
        output = []
        # access to Stack[-1]:
        output.append("@SP")
        output.append("A=M-1")
        output.append(self.symbols[command])

        output.append(" ")  # empty line for easier reading
        return output

    def write_pop_push(self, command: str, segment: str, index: int) -> list:
        """command is either 'pop' or 'push'.
        segment is a value/name"""
        output = []
        if command == "C_PUSH":
            return self.write_push(command, segment, index)
        elif command == "C_POP":
            return self.write_pop(command, segment, index)
        else:
            raise NameError("Unexpected Command Type")

    def write_push(self, command: str, segment: str, index: int) -> list:
        """writes push block"""
        output = []

        if segment == "constant":
            output.append("@" + str(index))
            output.append("D=A")
            output.append("@SP")
            output.append("AM=M+1")
            output.append("A=A-1")
            output.append("M=D")
        elif segment in ["local", "argument", "this", "that", "temp", "pointer"]:
            # put index value into D:
            output.append("@" + str(index))
            output.append("D=A")
            # put base value into A:
            if segment == "temp" or segment == "pointer":
                output.append(self.symbols[segment])
            else:
                # A = RAM[M], where is segment referring to
                output.append(self.symbols[segment])
                output.append("A=M")
            # calculate the source address into A:
            output.append("A=D+A")
            output.append("D=M")  # put source value into D
            # put D value into RAM[SP]:
            output.append("@SP")
            output.append("A=M")
            output.append("M=D")
            # increment stack pointer:
            output.append("@SP")
            output.append("M=M+1")
        elif segment == "static":
            # calculate the source address into A:
            output.append("@" + self.file_name + "." + str(index))
            output.append("D=M")  # put the source value into D
            # Put D value into RAM[SP]:
            output.append("@SP")
            output.append("A=M")
            output.append("M=D")
            # increment stack pointer
            output.append("@SP")
            output.append("M=M+1")
        else:
            raise NameError("Unexpected Push Segment")

        output.append("")  # empty line for easier reading
        return output

    def write_pop(self, command: str, segment: str, index: int) -> list:
        """writes pop block"""
        output = []

        if segment == "constant":  # invalid command.
            raise NameError("Cannot Pop Constant Segment")
        elif segment in ["local", "argument", "this", "that", "temp", "pointer"]:
            # put the index value into D:
            output.append("@" + str(index))
            output.append("D=A")
            # put base value into A:
            if segment == "temp" or segment == "pointer":
                output.append(self.symbols[segment])
            else:
                # A = RAM[M], where is segment referring to:
                output.append(self.symbols[segment])
                output.append("A=M")
            output.append("D=D+A")  # calculate source address into D
            # put D value into R13:
            output.append("@R13")
            output.append("M=D")
            # pop stack value into D:
            output.append("@SP")
            output.append("AM=M-1")
            output.append("D=M")
            # RAM[R13] = D:
            output.append("@R13")
            output.append("A=M")
            output.append("M=D")
        elif segment == "static":
            # pop stack value into D
            output.append("@SP")
            output.append("AM=M-1")
            output.append("D=M")
            output.append("@" + self.file_name + "." + str(index))  # put the source address into A
            output.append("M=D")
        else:
            raise NameError("Unexpected Pop Segment")

        output.append("")  # empty line for easier reading
        return output