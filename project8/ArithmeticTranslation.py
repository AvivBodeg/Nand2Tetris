from StackActionsTranslation import DEC_STACK, INC_STACK, D_TO_STACK, STACK_TO_D
ARITHMETIC_OPS = {'add', 'sub', 'and', 'or', 'not', 'eq', 'gt', 'lt', 'neg'}
UNARY_OPS_MAP = {'neg': 'M=-M',
                 'not': 'M=!M'}
BINARY_OPS_MAP = {'add': lambda _: 'D=D+M',
                  'sub': lambda _: 'D=D-M',
                  'and': lambda _: 'D=D&M',
                  'or': lambda _: 'D=D|M',
                  'eq': lambda x: comparison_op('JEQ', x),
                  'gt': lambda x: comparison_op('JGT', x),
                  'lt': lambda x: comparison_op('JLT', x)
                  }


def comparison_op(jump_condition: str, jump_num: str) -> str:
    """Returns instruction of the comparison operation provided, storing the result at D"""
    return '\n'.join([
        'D=D-M', f'@TRUE.{str(jump_num)}', f'D;{jump_condition}', f'(FALSE.{str(jump_num)})',
        'D=0', f'@END.{str(jump_num)}', '0;JMP', f'(TRUE.{str(jump_num)})',
        'D=-1', f'(False.{str(jump_num)})'
    ])


def arithmetic_logical_instruction(op: str, jump_num: int) -> str:
    """Returns instruction of the arithmetic operation provided"""
    if op in UNARY_OPS_MAP.keys():
        return '\n'.join([
            DEC_STACK, '@SP', 'A=M', UNARY_OPS_MAP[op], INC_STACK
        ])
    elif op in BINARY_OPS_MAP.keys():
        return '\n'.join([
            f'\n// {op}', DEC_STACK, STACK_TO_D, '@R15', 'M=D', DEC_STACK, STACK_TO_D,
            '@R15', BINARY_OPS_MAP[op](jump_num), D_TO_STACK, INC_STACK
        ])
    raise Exception(f'Invalid arithmetic operation: {op}')
