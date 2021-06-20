import sys
import re
import pandas as pd
import numpy as np
import self as self

from semantic import Semantic, error_manager

sys.path.append('../lexical')
sys.path.append('../utils')
sys.path.append('../grammar')
from lexical import Lex
from copy import deepcopy
from log import Log
from grammar import Gram, get_test_tokens
from error import *
from instruction import Instruction, InstructionManager

logger = Log("./logs/log.txt")
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)
# 设置value的显示长度为100，默认为50
pd.set_option('max_colwidth', 200)
pd.set_option('display.width', 5000)
from enum import Enum


def print_line(info):
    n = len(info)
    nstar = (100 - n) // 2
    extra_star = (100 - n) % 2
    print('*' * nstar, info, '*' * (nstar + extra_star))


class Op(Enum):
    label = 'label'
    goto = 'goto'
    jal = 'goto_save'
    exit = 'exit'
    assign = '='
    li = 'li'
    lv = 'lv'
    gt = '>'
    lt = '<'
    ge = '>='
    le = '<='
    eq = '=='
    mul = '*'
    sub = '-'
    add = '+'
    div = '/'
    bit_and = '&'
    bit_or = '|'
    logic_and = '&&'
    logic_or = '||'
    ret = 'return'
    put = 'put'
    get = 'get'


class CodeGenerator:
    def __init__(self, instructions):
        self.instructions = instructions
        self.mips_instructions = []
        self.regs = [i for i in range(7, -1, -1)]
        self.regs_status = dict()

    def get_reg(self, tmp):
        reg = self.regs[-1]
        del self.regs[-1]
        self.regs_status[tmp] = reg
        return reg

    def free_reg(self, tmp):
        reg = self.regs_status[tmp]
        del self.regs_status[tmp]
        self.regs.append(reg)
        return reg

    def mips_translate(self):
        # self.mips_instructions.append()
        self.mips_instructions.append(
            ".data\nprompt: .asciiz \"enter an integer : \"\nend: .asciiz \"\\n\"\n\n.text\n");
        for instruction in self.instructions:
            self.translate(instruction)
        self.mips_instructions.append("\nread:\nli $v0 4\nla $a0 prompt\nsyscall\nli $v0 5\nsyscall\njr $ra\n");
        self.mips_instructions.append("\nwrite:\nli $v0 1\nsyscall\nli $v0 4\nla $a0 end\nsyscall\njr $ra\n");
        fw = open('result/mips_code.txt', 'w')
        for inst in self.mips_instructions:
            print(inst, end='')
            fw.write(inst)

    def translate(self, inst):
        op = inst.op
        num1 = inst.num1
        num2 = inst.num2
        res = inst.res
        # print(res)
        if op == Op.label.value:
            self.mips_instructions.append(f'\n{res}:\n')
            if res.startswith('main_body'):
                self.mips_instructions.append("\nmove $s0 $ra\n")
        elif op == Op.li.value:
            reg = self.get_reg(res)
            self.mips_instructions.append(f'li $t{reg} {num1}\n')
        elif op == Op.lv.value:
            reg = self.get_reg(res)
            offset = num1
            self.mips_instructions.append(f'lw $t{reg} {offset}($sp)\n')
        elif op == Op.mul.value:
            reg2, reg1 = self.free_reg(num2), self.free_reg(num1)
            self.mips_instructions.append(f'mult $t{reg1} $t{reg2}\n')
            reg3 = self.get_reg(res)
            self.mips_instructions.append(f'mflo $t{reg3}')
        elif op == Op.div.value:
            reg2, reg1 = self.free_reg(num2), self.free_reg(num1)
            self.mips_instructions.append(f'div $t{reg1} $t{reg2}\n')
            reg3 = self.get_reg(res)
            self.mips_instructions.append(f'mflo $t{reg3}')
        elif op == Op.add.value:
            reg2, reg1 = self.free_reg(num2), self.free_reg(num1)
            reg3 = self.get_reg(res)
            self.mips_instructions.append(f'add $t{reg3} $t{reg1} $t{reg2}\n')

        elif op == Op.sub.value:
            reg2, reg1 = self.free_reg(num2), self.free_reg(num1)
            reg3 = self.get_reg(res)
            self.mips_instructions.append(f'sub $t{reg3} $t{reg1} $t{reg2}\n')

        elif op == Op.assign.value:
            offset = res
            if num1 == '0':
                self.mips_instructions.append(f'sw $zero {offset}($sp)\n')
            else:
                reg = self.free_reg(num1)
                self.mips_instructions.append(f'sw $t{reg} {offset}($sp)\n')
        elif op == Op.goto.value:
            self.mips_instructions.append(f'j {res}\n')
        elif op == Op.jal.value:
            self.mips_instructions.append(f'jal {res}\n')
        elif op == Op.exit.value:
            self.mips_instructions.append(f'li $v0 10\n')
            self.mips_instructions.append(f'syscall\n')
        elif op == Op.eq.value:
            reg2, reg1 = self.free_reg(num2), self.free_reg(num1)
            self.mips_instructions.append(f'beq $t{reg1} $t{reg2} {res}\n')
        elif op == Op.gt.value:
            reg2, reg1 = self.free_reg(num2), self.free_reg(num1)
            self.mips_instructions.append(f'bgt $t{reg1} $t{reg2} {res}\n')
        elif op == Op.lt.value:
            reg2, reg1 = self.free_reg(num2), self.free_reg(num1)
            self.mips_instructions.append(f'blt $t{reg1} $t{reg2} {res}\n')
        elif op == Op.ge.value:
            reg2, reg1 = self.free_reg(num2), self.free_reg(num1)
            self.mips_instructions.append(f'bge $t{reg1} $t{reg2} {res}\n')
        elif op == Op.le.value:
            reg2, reg1 = self.free_reg(num2), self.free_reg(num1)
            self.mips_instructions.append(f'ble $t{reg1} $t{reg2} {res}\n')
        elif op == Op.ret.value:
            reg = self.free_reg(res)
            self.mips_instructions.append(f'move $v0 $t{reg}\n')
            self.mips_instructions.append(f'move $ra $s0\n')
            self.mips_instructions.append(f'jr $ra\n')
        elif op == Op.get.value:
            offset = res
            self.mips_instructions.append(f'jal read\n')
            self.mips_instructions.append(f'sw $v0 {offset}($sp)\n')
        elif op == Op.put.value:
            reg = self.free_reg(res)
            self.mips_instructions.append(f'move $a0 $t{reg}\n')
            self.mips_instructions.append(f'jal write\n')
        elif op == Op.bit_and.value:
            reg2, reg1 = self.free_reg(num2), self.free_reg(num1)
            reg3 = self.get_reg(res)
            self.mips_instructions.append(f'and $t{reg3} $t{reg1} $t{reg2}\n')
        elif op == Op.bit_or.value:
            reg2, reg1 = self.free_reg(num2), self.free_reg(num1)
            reg3 = self.get_reg(res)
            self.mips_instructions.append(f'or $t{reg3} $t{reg1} $t{reg2}\n')


if __name__ == '__main__':
    # test()
    lex = Lex()
    tokens = get_test_tokens("./test_case/basic_test2.cpp")

    grammar = Gram("../grammar/cfg_resource/cfg_v8.txt")
    grammar.parse(tokens, pr=True)
    if grammar.err:
        print('grammar error.')

    else:
        semantic = Semantic(grammar.tree)
        semantic.run()

        semantic.print_variable_table()
        semantic.print_function_table()
        error_manager.print()

        #         生成代码
        cg = CodeGenerator(semantic.instruction_manager.instructions)
        cg.mips_translate()
