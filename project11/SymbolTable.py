from CONSTANTS import GLOBAL


class SymbolTable:
    def __init__(self):
        self.global_scope = {}
        self.subroutine_scope = {}
        self.current_scope = self.global_scope
        self.field_counter = 0
        self.static_counter = 0
        self.variable_counter = 0
        self.argument_counter = 0
        self.if_counter = 0
        self.while_counter = 0

    def get_index(self, name):
        """gets the index of a given  variable name"""
        if name in self.current_scope:
            return self.current_scope[name][2]
        if name in self.global_scope:
            return self.global_scope[name][2]
        return 'None'

    def set_scope(self, name):
        """sets the current scope"""
        if name == GLOBAL:
            self.current_scope = self.global_scope
        else:
            self.current_scope = self.subroutine_scope

    def reset(self, subroutine_name):
        """resets the symbol table and prepares for a new subroutine"""
        self.variable_counter = 0
        self.argument_counter = 0
        self.while_counter = 0
        self.if_counter = 0
        self.subroutine_scope[subroutine_name] = {}

    def define(self, name, type_, kind):
        if kind == 'static':
            self.global_scope[name] = (type_, kind, self.static_counter)
            self.static_counter += 1
        elif kind == 'field':
            self.subroutine_scope[name] = (type_, kind, self.field_counter)
            self.field_counter += 1
        elif kind == 'arg':
            self.subroutine_scope[name] = (type_, kind, self.argument_counter)
            self.argument_counter += 1
        elif kind == 'var':
            self.subroutine_scope[name] = (type_, kind, self.variable_counter)
            self.variable_counter += 1

    def type_of(self, name):
        if name in self.current_scope:
            return self.current_scope[name][0]
        if name in self.global_scope:
            return self.global_scope[name][0]
        return 'None'

    def kind_of(self, name):
        """returns the kind of variable"""
        if name in self.current_scope:
            return self.current_scope[name][1]
        if name in self.global_scope:
            return self.global_scope[name][1]
        return 'None'

    def index_of(self, name):
        if name in self.current_scope:
            return self.current_scope[name][2]
        if name in self.global_scope:
            return self.global_scope[name][2]
        return 'None'

    # TODO: might have to replace with 'len([var for (key, var) in self.current_scope.items() if kind == var[1]])'
    def count_variables(self, kind):
        """returns the number of variables of a specific kind in the current scope"""
        return len([var for var in self.current_scope.values() if kind == var[1]])

    def count_variables_globally(self, kind):
        """returns the number of variables of a specific kind in the global scope"""
        return len([var for var in self.global_scope.values() if kind == var[1]])
