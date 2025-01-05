class SymbolTable:
    def __init__(self):
        self.symbol_table = self.initialize_symbol_table()
        self.next_var_address = 16

    @staticmethod
    def initialize_symbol_table():
        """Initializes the symbol table with predefined Hack symbols"""
        symbol_table = {
            'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4,
            'SCREEN': 16384, 'KBD': 24576
        }
        for i in range(16):
            symbol_table[f'R{i}'] = i
        return symbol_table

    def get_address(self, symbol) -> int:
        """Returns the address (int) associated with symbol if it exists,
        else adds it to the symbol table and increments @next_variable_address
        """
        if symbol in self.symbol_table:
            return self.symbol_table[symbol]
        else:
            self.symbol_table[symbol] = self.next_var_address
            self.next_var_address += 1
            return self.symbol_table[symbol]

    def set_loop(self, label, address):
        self.symbol_table[label] = address

    def print_table(self):
        """Prints all items in @symbol_table"""
        for symbol in self.symbol_table:
            print(f"{symbol}:{self.symbol_table[symbol]}")
