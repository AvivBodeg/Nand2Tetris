from StackActionsTranslation import (DEC_STACK, INC_STACK, D_TO_STACK,
                                     STACK_TO_D, push_constant, push_pointer)


def label(name: str, function: str) -> str:
    """creates label instruction"""
    return f'\n({function}${name})'


def goto_instruction(name: str, function: str) -> str:
    return  f'@{function}${name}\n0;JMP'


def conditional_goto_instruction(name: str, function: str) -> str:
    return '\n'.join(['// if-goto instruction', DEC_STACK, STACK_TO_D,
                      f'@{function}${name}', 'D;JNE'])


def call_instruction(caller: str, called_func: str, args: int, return_tag) -> str:
    """Creates instruction to call called_func with agrs arguments.
    return address and segment pointers are temporarily pushed into the stack
    while ARG and LCL are being updated"""
    return '\n'.join([
        f'\n/// call {called_func} {args} ///',
        push_constant(f'{caller}$ret.{return_tag}'), # store return address in stack
        # store segment pointers in stack
        push_pointer('local'),
        push_pointer('argument'),
        push_pointer('this'),
        push_pointer('that'),
        '// rebase ARG=SP-5-args',
        '@SP', 'D=M', f'@{args+5}', 'D=D-A', '@ARG', 'M=D',
        '// rebase LCL=SP',
        '@SP', 'D=M', '@LCL', 'M=D',
        # jummp to called_func and add return label
        f'@{called_func}', '0;JMP', f'({caller}$ret.{return_tag})'
    ])


def function_instruction(function: str, varsNum: int) -> str:
    """Creates instruction for defining a with vars local variables."""
    instruction = [f'({function})', '// init local variables']
    # init local variables as 0
    for i in range(varsNum):
        instruction.append(push_constant('0'))
    return '\n'.join(instruction)


def offsetted_R13_value(offset: int) -> str:
    """Creates instruction for offsetting the address in R13 by -offset.
     placing the value of RAM[R13-offset] into D"""
    if offset < 1:
        raise Exception('Invalid offset')
    # edge case
    if offset == 1:
        instruction = ['@R13', 'A=M-1', 'D=M']
    else:
        instruction = ['@R13', 'D=M', f'@{offset}', 'A=D-A', 'D=M']
    return '\n'.join(instruction)


def return_instruction() -> str:
    """Creates instruction for returning from a function.
    the return value in the stack of the caller"""
    return '\n'.join([
        '\n/// returning instruction ///',
        '// R13 = end address',
        '@LCL', 'D=M', '@R13', 'M=D',
        '// R14 = return, ADDRESS=RAM[R13 - 5]',
        '@5', 'A=D-A', 'D=M', '@R14', 'M=D',
        '// RAM[@ARG] = return value',
        DEC_STACK, STACK_TO_D,  # return value is set to the top of a stack
        '@ARG', 'A=M', 'M=D',
        '// SP=ARG+1',
        '@ARG', 'D=M+1', '@SP', 'M=D',
        '// pop stack segments pointers',
        offsetted_R13_value(1), '@THAT', 'M=D',
        offsetted_R13_value(2), '@THIS', 'M=D',
        offsetted_R13_value(3), '@ARG', 'M=D',
        offsetted_R13_value(4), '@LCL', 'M=D',
        '// jump back to caller',
        '@R14', 'A=M', '0;JMP'
    ])
