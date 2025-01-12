class VMWriter:
    def __init__(self, output_file):
        self.output_file = output_file

    def write_push(self, segment, index):
        with open(self.output_file, 'a') as out_file:
            out_file.write(f'push {segment} {index}\n')

    def write_pop(self, segment, index):
        with open(self.output_file, 'a') as out_file:
            out_file.write(f'pop {segment} {index}\n')

    def write_arithmetic(self, command):
        with open(self.output_file, 'a') as out_file:
            out_file.write(f'{command}\n')

    def write_label(self, label):
        with open(self.output_file, 'a') as out_file:
            out_file.write(f'label {label}\n')

    def write_goto(self, label):
        with open(self.output_file, 'a') as out_file:
            out_file.write(f'goto {label}\n')

    def write_if_goto(self, label):
        with open(self.output_file, 'a') as out_file:
            out_file.write(f'if-goto {label}\n')

    def write_call(self, name, nArgs):
        with open(self.output_file, 'a') as out_file:
            out_file.write(f'call {name} {nArgs}\n')

    def write_function(self, name, nVars):
        with open(self.output_file, 'a') as out_file:
            out_file.write(f'function {name} {nVars}\n')

    def write_return(self):
        with open(self.output_file, 'a') as out_file:
            out_file.write(f'return\n')
