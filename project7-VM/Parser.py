class Parser:
    def __init__(self, file_name: str):
        self.current_cmd = ''
        self.curr_index = -1
        self.input_file = file_name
        self.commands = []
        self.parse_file()

    def parse_file(self):
        """Initializes @self.commands list with cleand lines"""
        with open(self.input_file, 'r') as file_lines:
            for line in file_lines:
                cleaned_line = line.split('//')[0]  # remove comments
                cleaned_line = cleaned_line.strip()  # remove extra whitespaces
                if cleaned_line:  # line isn't empty after cleaning
                    self.commands.append(cleaned_line)

    @staticmethod
    def command_type(current_command) -> str:
        """Returns the type of the current command."""
        arithmetic_commands = ["add", "sub", "neg", "and", "or",
                               "not", "eq", "gt", "lt"]
        command = current_command.split(" ")[0]
        # Determine the type of the current command.
        if command in arithmetic_commands:
            return "C_ARITHMETIC"
        elif command == "push":
            return "C_PUSH"
        elif command == "pop":
            return "C_POP"
        else:
            # project8 commands / error
            raise NameError("Unexpected Command Type")

    def get_argument1(self, current_command) -> str:
        """Returns the first argument of the current command."""
        command_type = self.command_type(current_command)
        if command_type == "C_ARITHMETIC":
            return current_command.split(' ')[0]  # returns the command itself
        else:
            return current_command.split(' ')[1]  # returns stack

    @staticmethod
    def get_argument2(current_command) -> int:
        """Returns the second argument of the current command.
        only for C_POP, C_PUSH and project 8 commands"""
        return int(current_command.split(' ')[2])
