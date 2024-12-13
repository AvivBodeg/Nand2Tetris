# Repeating Instructions:
DEC_STACK = '\n'.join(['// SP-=1', '@SP', 'M=M-1'])
INC_STACK = '\n'.join(['// SP+=1', '@SP', 'M=M+1'])
D_TO_STACK = '\n'.join(['// RAM[SP]=D', '@SP', 'A=M', 'M=D'])
STACK_TO_D = '\n'.join(['// D=RAM[SP]', 'A=M', 'D=M'])

# Constants:
SEGMENT_POINTERS = {
    'local': '@LCL',
    'argument': '@ARG',
    'this': '@THIS',
    'that': '@THAT'
}


def offset_pointer_to_D(segment: str, offset: str) -> str:
    """Creates instruction to offset SEG_MAP[segment] and store it in D"""
    return '\n'.join(['// D=RAM[segment]+offset', '@'+offset, 'D=A',
                      SEGMENT_POINTERS[segment], 'D=D+M'])


### PUSH ###
def push_instruction(segment: str, offset: str, static_name: str) -> str:
    """Creates instruction to push the data at the offset to the relevant segment"""
    instruction = f'\n/// push {segment} {offset} ///\n'
    if segment == 'constant':
        return instruction + push_constant(offset)
    elif segment == 'static':
        return instruction + push_static(static_name, offset)
    elif segment == 'pointer':
        if offset == '0':
            return instruction + push_pointer('this')
        elif offset == '1':
            return instruction + push_pointer('that')
        else:
            raise Exception('Invalid Syntax')
    elif segment == 'temp':
        return instruction + push_temp(offset)
    return instruction + push_segment(segment, offset)


def push_constant(const: str) -> str:
    """Creates instruction to push a constant"""
    return '\n'.join([
        '// D=' + const, '@' + const, 'D=A', D_TO_STACK, INC_STACK
    ])


def push_static(static_name: str, index: str) -> str:
    """Creates instruction to push as static at static_name.index"""
    return '\n'.join([
        f'// D=RAM[@{static_name}.{index}]', f'@{static_name}.{index}', 'D=M', D_TO_STACK, INC_STACK
    ])


def push_pointer(segment: str) -> str:
    """Creates instruction to push the pointer @segment"""
    return '\n'.join([
        '// D=@segment', SEGMENT_POINTERS[segment], 'D=M', D_TO_STACK, INC_STACK
    ])


def push_temp(offset: str) -> str:
    """Creates instruction to push the data at R5+offset"""
    return '\n'.join([
        '// @(5+offset)', '@' + str(int(offset) + 5),'D=M', D_TO_STACK, INC_STACK
    ])


def push_segment(segment: str, offset: str) -> str:
    """Creates instruction to push data from provided segment"""
    return '\n'.join([
        offset_pointer_to_D(segment, offset), '// D=RAM[D]', 'A=D', 'D=M', D_TO_STACK, INC_STACK
    ])


### POP ###
def pop_instruction(segment: str, offset: str, static_name: str) -> str:
    """Creates instruction to pop the data at the stack to offset @segment"""
    instruction = f'\n// pop {segment} {offset} //\n'
    if segment == 'temp':
        return instruction + pop_temp(offset)
    elif segment == 'static':
        return instruction + pop_static(static_name, offset)
    elif segment == 'pointer':
        if offset == "0":  # this=0
            return instruction + pop_pointer("this")
        elif offset == "1":  # that=1
            return instruction + pop_pointer("that")
        else:
            raise Exception("invalid syntax")
    return instruction + pop_other(segment, offset)


def pop_temp(offset: str) -> str:
    """Creates instruction to pop the data in the stack to R5+offset"""
    return '\n'.join([
        '// pop temp', DEC_STACK, STACK_TO_D, '@' + str(int(offset) + 5), 'M=D'
    ])


def pop_static(static_name: str, index: str) -> str:
    """Creates instruction to pop the data in the stack to var @name.index"""
    return '\n'.join([
        '// pop static', DEC_STACK, STACK_TO_D, f'// RAM[@{static_name}.{index}=D',
        f'@{static_name}.{index}', 'M=D'
    ])


def pop_pointer(segment: str) -> str:
    """Creates instruction to pop the data in the stack to @segment"""
    return '\n'.join([
        '// pop pointer', DEC_STACK, STACK_TO_D, f'// @{segment}=D', SEGMENT_POINTERS[segment], 'M=D'
    ])


def pop_other(segment: str, offset: str) -> str:
    """Creates instruction to pop the data in the stack to segment"""
    return '\n'.join([
        offset_pointer_to_D(segment, offset), '//@address=D', '@address', 'M=D',
        DEC_STACK, STACK_TO_D, '// RAM[address]=D', '@address', 'A=M', 'M=D'
    ])
