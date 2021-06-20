import sys
import re
import pandas as pd
import numpy as np
import self as self

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


class TYPE(Enum):
    bool = "bool"
    int = "int"
    char = "char"
    void = "void"
    struct = "struct"

    def __repr__(self):
        return 'TYPE.' + self._value_


class Variable:
    cur_offset = 0

    def __init__(self, tp=None, val=None, id=None, pos=(0, 0), struct_type=None, reg=None):
        self.id = id
        self.type = tp
        self.val = val
        self.pos = pos
        self.struct_type = struct_type
        self.offset = Variable.cur_offset
        Variable.cur_offset -= 4
        self.reg = reg

    def __add__(self, other):
        return Variable(self.type, self.val + other.val)

    def __sub__(self, other):
        return Variable(self.type, self.val - other.val)

    def __mul__(self, other):
        return Variable(self.type, self.val * other.val)

    def __floordiv__(self, other):
        return Variable(self.type, self.val // other.val)

    def __eq__(self, other):
        return Variable(TYPE.bool, self.val == other.val)

    def __lt__(self, other):
        return Variable(TYPE.bool, self.val < other.val)

    def __gt__(self, other):
        return Variable(TYPE.bool, self.val > other.val)

    def __le__(self, other):
        return Variable(TYPE.bool, self.val <= other.val)

    def __ge__(self, other):
        return Variable(TYPE.bool, self.val >= other.val)

    def logic_or(self, other):
        return Variable(TYPE.bool, self.val or other.val)

    def logic_and(self, other):
        return Variable(TYPE.bool, self.val and other.val)

    def __repr__(self):
        vid = self.id + ',' if self.id else ''
        st = ' ' + self.struct_type + ',' if self.struct_type else ''
        return "({}{}{},{})".format(vid, self.type, st, self.val)

    def bit_and(self, other):
        return Variable(TYPE.int, self.val & other.val)

    def bit_or(self, other):
        return Variable(TYPE.int, self.val | other.val)

    def logic_not(self):
        return Variable(TYPE.bool, not self.val)


class VariableManager:
    def __init__(self):
        self.variables = {}

    def contains(self, scope, v):
        return scope in self.variables and v in self.variables[scope]

    def delete_scope(self, scope):
        del self.variables[scope]

    def delete_variable(self, scope, v):
        del self.variables[scope][v]

    def get_variable(self, scope, v):
        # print('scope', scope, 'v', v)
        return self.variables[scope][v]

    def find_variable(self, scope_list, v):
        for scope in scope_list[::-1]:
            if self.contains(scope, v):
                return scope, self.variables[scope][v]
        return -1

    def add_variable(self, scope, v, tp, pos=(0, 0), struct_type=None):
        if self.contains(scope, v):
            old = self.variables[scope][v]
            err = Error(AlreadyDefinedVar(v, old.pos), pos)
            error_manager.add_error(err)
            return self.variables[scope][v]
        if scope not in self.variables:
            self.variables[scope] = {}
        self.variables[scope][v] = Variable(tp=TYPE(tp), id=v, pos=pos, struct_type=struct_type)
        return None

    def set_variable(self, scope, v, v_obj, pos):
        old_v = self.get_variable(scope, v)
        if v_obj.type != old_v.type:
            err = Error(IncompatibleType(v, old_v.type, v_obj.type), pos)
            error_manager.add_error(err)
            # print("{} {} cannot assign\n".format(old_v, v_obj))
            return -1
        if v_obj.val is None:
            err = Error(UninitializedVar(v), pos)
            error_manager.add_error(err)
            # print("{} not initialized\n".format(v_obj))
            return -1
        old_v.val = v_obj.val

    def check_struct_field(self, scope, struct_name):
        if not self.contains(scope, struct_name):
            return None
        struct_field_vars = self.variables[scope][struct_name]
        defined_vars = []
        for var_obj in struct_field_vars:
            if self.contains(scope, var_obj[1][0]):
                defined_vars.append(var_obj)
        return defined_vars

    def op_variable(self, x, op, y, pos):
        err_type = None
        if x.val is None:
            err = Error(UninitializedVar(x.id), pos)
            error_manager.add_error(err)
            # print("{} not initialized".format(x))
            err_type = 1
        if y.val is None:
            err = Error(UninitializedVar(x.id), pos)
            error_manager.add_error(err)
            # print("{} not initialized".format(y))
            err_type = 1
        if x.type != y.type:
            err = Error(MismatchedType(x.type, y.type, op), pos)
            error_manager.add_error(err)
            # print("cannot op \n")
            err_type = 2
        if err_type:
            return None
        # valid type check
        # check bool
        if x.type == TYPE.bool:
            if op in ['+', '-', '*']:
                err = Error(UnsupportedOperation(x.id, x.type, op), pos)
                error_manager.add_error(err)
                # print("type {} cannot operator {}".format(x.type, op))
                return None
        if x.type == TYPE.int:
            # if op in ['&', '|']:
            if op in []:
                err = Error(UnsupportedOperation(x.id, x.type, op), pos)
                error_manager.add_error(err)
                # print("type {} cannot operator {}".format(x.type, op))
                return None
        if op == '+':
            return x + y
        elif op == '-':
            return x - y
        elif op == '*':
            return x * y
        elif op == '/':
            return x // y
        elif op == '==':
            return x == y
        elif op == '<':
            return x < y
        elif op == '<=':
            return x <= y
        elif op == '>':
            return x > y
        elif op == '>=':
            return x >= y
        elif op == '<>':
            return not (x == y)
        elif op == '||':
            print('hello')
            print(x, y, x.logic_or(y))
            return x.logic_or(y)
        elif op == '&&':
            return x.logic_and(y)
        elif op == '&':
            return x.bit_and(y)
        elif op == '|':
            return x.bit_or(y)

    def __str__(self):
        res = []
        for v_obj in self.variables.values():
            res.append(str(v_obj))
        return "\n".join(res)

    def set_struct_field(self, cur, var_name, var_list, pos):
        self.variables[cur][var_name] = var_list

    def set_struct_attribute(self, cur, scopes, var_name, attribute, v_obj, pos):
        _, stu = self.find_variable(scopes, var_name)
        stu_type = stu.struct_type
        # check whether to assign
        scope, field_list = self.find_variable(scopes, stu_type)
        for t in field_list:
            if t[1][0] == attribute:
                if t[0] == v_obj.type:
                    if self.variables[cur][var_name].val is None:
                        self.variables[cur][var_name].val = {}
                    self.variables[cur][var_name].val[attribute] = v_obj
                    return
                else:
                    err = Error(IncompatibleType(f'{var_name}.{attribute}', t[0], v_obj.type), pos)
                    error_manager.add_error(err)
                    return

        err = Error(UndefinedError(f'{var_name}.{attribute}'), pos)
        error_manager.add_error(err)
        return

    def op_variable_single(self, op, v_obj, pos):
        if op == '!':
            return v_obj.logic_not()


class Function:
    def __init__(self, ret_type, name, params, pos=None):
        self.ret_type = ret_type
        self.name = name
        self.params = params
        self.pos = pos

    def __repr__(self):
        return "{} {} {}".format(self.ret_type, self.name, str(self.params))


class FunctionManager:
    def __init__(self):
        self.func_map = {}

    def add_func(self, ret_type, func_name, params, pos=None):
        if func_name in self.func_map:
            first_pos = self.func_map[func_name].pos
            err = Error(AlreadyDefinedFunc(func_name, first_pos), pos)
            error_manager.add_error(err)
            return -1
        self.func_map[func_name] = Function(ret_type, func_name, params, pos)

    def __repr__(self):
        ret = []
        for func in self.func_map.values():
            ret.append(str(func))
        return '\n'.join(ret)

    def get(self, func_name, pos):
        if func_name in self.func_map:
            return self.func_map[func_name]
        err = Error(UndefinedFuncError(func_name), pos)
        error_manager.add_error(err)
        return None

    def params_match(self, func_name, params, pos):
        func = self.func_map[func_name]
        std_params = [e for e in func.params]
        # print(std_params, params)
        if std_params == params:
            return True

        err = Error(MismatchedParams(func_name, params, std_params), pos)
        error_manager.add_error(err)
        return False


class ScopeManager:
    def __init__(self):
        self.scopes = []
        self.cur = 0
        self.gl = 0
        self.max_scope = 0

    def go_scope(self):
        self.max_scope += 1
        self.cur = self.max_scope
        self.scopes.append(self.cur)

    def out_scope(self):
        self.scopes.pop(-1)
        self.cur = self.scopes[-1]

    def set_global(self, gl):
        self.gl = gl

    def set_scope(self, s):
        self.scope = s


def pr_child(node):
    print('-' * 100)
    for ch in node.child:
        print(ch)
    print('-' * 100)


def new_label(key, kid):
    return key + '_' + str(kid)


class Semantic:
    def __init__(self, tree):
        self.tree = tree
        self.error_manager = ErrorManager()
        self.variable_manager = VariableManager()
        self.function_manager = FunctionManager()
        self.scope_manager = ScopeManager()
        self.instruction_manager = InstructionManager()
        self.init_function_manager()

    def run(self):
        self.tree.print()
        self.proc_program(self.tree.root)
        self.instruction_manager.print()

    def proc_program(self, root):
        self.scope_manager.set_global(0)
        self.scope_manager.go_scope()
        self.proc_func_or_dec_list(root.child[0])

    def proc_func_or_dec_list(self, node):
        if node.child[0].is_valid():
            self.proc_func_or_dec(node.child[0])
            self.proc_func_or_dec_list(node.child[1])

    def proc_func_or_dec(self, node):
        if node.child[0].data == '类型变量':
            tp, var = self.proc_type_var(node.child[0])
            self.instruction_manager.add_instruction('label', "", "", var)

            self.proc_param_impl_or_var_dec(node.child[1], tp, var)

        else:
            self.proc_struct_field_stmt(node.child[0])

    def proc_type_var(self, node):
        tp = self.proc_type(node.child[0])
        var, pos, attribute = self.proc_var(node.child[1])
        self.variable_manager.add_variable(self.scope_manager.cur, var, tp, pos)
        return tp, var

    def proc_type(self, node):
        return node.child[0].data

    def proc_var(self, node):
        if node.child[0].data == '标志符':
            sym, pos, attribute = self.proc_user_symbol(node.child[0])
        else:
            attribute = None
            sym, pos = self.proc_system_symbol(node.child[0])
        return sym, pos, attribute

    def proc_user_symbol(self, node):
        var_name, pos = node.child[0].symbol, node.child[0].pos
        attribute = self.proc_symbol_attribute(node.child[1])
        if not attribute:
            return var_name, pos, None
        return var_name, pos, attribute

    def proc_symbol_attribute(self, node):
        if node.child[0].is_valid():
            return node.child[1].symbol
        return None

    def proc_system_symbol(self, node):
        # 标准库函数
        return node.child[0].data, node.child[0].pos

    def proc_param_impl_or_var_dec(self, node, tp, var):
        if node.child[0].data == '(':
            label_func = new_label(f'{var}_body', node.id)
            self.instruction_manager.add_instruction('goto_save', "", "", label_func)
            # 如果判断为函数，则需要将 变量表 中的变量拿出来，放进函数表中
            self.variable_manager.delete_variable(self.scope_manager.cur, var)
            self.scope_manager.go_scope()
            # print('cur', self.scope_manager.cur, end='\n')
            params = self.proc_param_dec(node.child[1])
            self.function_manager.add_func(TYPE(tp), var, params, node.child[0].pos)

            label_exit = new_label('exit', node.id)
            self.instruction_manager.add_instruction('exit', "", "", label_exit)
            # 要进入代码段了

            self.instruction_manager.add_instruction('label', "", "", label_func)
            self.proc_func_impl(node.child[3])

        else:
            # print(node.child)
            self.proc_global_var_closure(node.child[0], tp)

    def proc_global_var_closure(self, node, tp):
        for child in node.child:
            if child.data == ';':
                break
            elif child.data == '变量':
                var_name, pos, _ = self.proc_var(child)
                self.variable_manager.add_variable(self.scope_manager.cur, var_name, tp, pos)
            elif child.data == '全局变量闭包':
                self.proc_global_var_closure(child, tp)

    def proc_param_dec(self, node):
        params = []
        if node.child[0].is_valid():
            tp, var = self.proc_dec(node.child[0])
            params.append((TYPE(tp), var))
            params = self.proc_dec_closure(node.child[1], params)

        return params

    def proc_dec(self, node):
        tp = self.proc_type(node.child[0])
        var_name, pos, attribute = self.proc_var(node.child[1])
        self.variable_manager.add_variable(self.scope_manager.cur, var_name, tp, pos)
        self.proc_init_value(node.child[2], var_name)
        return TYPE(tp), var_name

    def proc_init_value(self, node, v):
        if node.child[0].data == '=':
            v_obj = self.proc_rvalue(node.child[1])
            # 赋值
            if v_obj:
                self.assign_value(v, v_obj, node.child[0].pos)
                scope, obj = self.find_near_variable(v)
                offset = obj.offset
                # print('bug:', v_obj.reg)
                self.instruction_manager.add_instruction('=', v_obj.reg, "", str(offset))
        else:
            offset = self.variable_manager.get_variable(self.scope_manager.cur, v).offset
            self.instruction_manager.add_instruction('=', "0", "", str(offset))
            return

    def proc_rvalue(self, node) -> Variable:
        return self.proc_exp(node.child[0])

    def proc_exp(self, node):
        v_obj = self.proc_factor_item(node.child[0])
        v_item = self.proc_item(node.child[1], v_obj)
        # print('proc_exp', v_item.reg)
        return v_item

    def proc_factor_item(self, node):
        v_obj = self.proc_factor_exp(node.child[0])
        return self.proc_factor_exp_closure(node.child[1], v_obj)

    def proc_item(self, node, item):

        if node.child[0].is_valid():
            v_obj = self.proc_factor_item(node.child[1])
            op = node.child[0].data
            old_reg = item.reg
            # print('op', op, 'num1', item, 'num2', v_obj)
            item = self.variable_manager.op_variable(item, op, v_obj, node.child[0].pos)
            item = self.proc_item(node.child[2], item)
            res = self.instruction_manager.get_temp_reg()
            item.reg = res
            self.instruction_manager.add_instruction(op, old_reg, v_obj.reg, res)
            return item
        return item

    def find_near_variable(self, var_name):
        return self.variable_manager.find_variable(self.scope_manager.scopes, var_name)

    def proc_factor_exp(self, node):
        if node.child[0].is_terminal():  # (表达式)
            return self.proc_exp(node.child[1])
        elif node.child[0].data == '数字':
            num = self.proc_digit(node.child[0])
            res = self.instruction_manager.get_temp_reg()
            # print('res', res)
            # print('debug num', num)
            self.instruction_manager.add_instruction('li', num, "", res)
            return Variable(TYPE.int, num, reg=res)
        elif node.child[0].data == '布尔值':
            bool_value = self.proc_bool_value(node.child[0])
            return Variable(TYPE.bool, bool_value)
        elif node.child[0].data == '变量':
            var_name, pos, attr = self.proc_var(node.child[0])
            if not node.child[1].child[0].is_valid():
                if not self.var_defined(var_name):
                    return None
                if attr is None:
                    scope, v_obj = self.find_near_variable(var_name)
                    res = self.instruction_manager.get_temp_reg()
                    offset = v_obj.offset
                    self.instruction_manager.add_instruction('lv', str(offset), "", res)
                    v_obj.reg = res
                    return v_obj
                else:
                    _, v_obj = self.find_near_variable(var_name)
                    v_attr = v_obj.val[attr]
                    return v_attr
            else:

                v_obj_list = self.proc_func_call_param(node.child[1])
                # TODO 处理函数调用结果计算
                # print('v_obj_list', v_obj_list)
                func_name = var_name
                func = self.function_manager.get(func_name, pos)
                if not func:
                    return None
                # 确定参数类型是否匹配
                params_list = [e.type for e in v_obj_list]

                if not self.function_manager.params_match(func_name, params_list, pos):
                    # print(f"{func_name} parameter mis match")
                    return None
                return Variable(tp=func.ret_type)

    def proc_factor_exp_closure(self, node, factor_exp):
        if node.child[0].is_valid():
            v_obj = self.proc_factor_exp(node.child[1])

            factor_exp = self.variable_manager.op_variable(factor_exp, node.child[0].data, v_obj, node.child[0].pos)
            factor_exp = self.proc_factor_exp_closure(node.child[2], factor_exp)
            return factor_exp
        else:
            return factor_exp

    def proc_digit(self, node):
        return node.child[0].symbol
        pass

    def proc_func_call_param(self, node) -> list:
        if node.child[0].data == '(':
            return self.proc_param_list(node.child[1])
        else:
            return None

    def proc_param_list(self, node, func_name=None):
        v_obj = self.proc_param(node.child[0], func_name)
        v_obj_list = self.proc_param_closure(node.child[1], [v_obj], func_name)
        return v_obj_list

    def proc_param(self, node, func_name):
        if node.child[0].data == '标志符':
            var_name, pos, _ = self.proc_user_symbol(node.child[0])
            scope, v_obj = self.find_near_variable(var_name)
            if func_name is None:
                res = self.instruction_manager.get_temp_reg()
                offset = v_obj.offset
                self.instruction_manager.add_instruction('lv', str(offset), "", res)
                v_obj.reg = res

            return v_obj
        elif node.child[0].data == '数字':
            num = self.proc_digit(node.child[0])
            if func_name is None:
                res = self.instruction_manager.get_temp_reg()
                # print('error', num)
                self.instruction_manager.add_instruction('li', num, "", res)
            return Variable(TYPE.int, num, reg=res)

        elif node.child[0].data == '布尔值':
            return self.proc_digit(node.child[0])

    def proc_param_closure(self, node, v_obj_list, func_name):
        if node.child[0].data == ',':
            val = self.proc_param(node.child[1], func_name)
            v_obj_list.append(val)
            return self.proc_param_closure(node.child[2], v_obj_list,func_name)
        else:
            return v_obj_list

    def proc_func_impl(self, node):
        if node.child[0].data == ';':
            self.scope_manager.out_scope()
            return
        elif node.child[0].data == '{':
            self.proc_func_body(node.child[1])
            self.scope_manager.out_scope()

    def proc_func_body(self, node):
        self.proc_func_body_closure(node.child[0])

    def proc_func_body_closure(self, node):

        if node.child[0].data == '声明语句':
            self.proc_dec_stmt(node.child[0])
        elif node.child[0].data == '赋值函数':
            self.proc_assign_func(node.child[0])
        elif node.child[0].data == 'while循环':
            self.proc_while_loop(node.child[0])
        elif node.child[0].data == 'if语句':
            self.proc_if_stmt(node.child[0])
        elif node.child[0].data == '空语句':
            self.proc_empty_stmt(node.child[0])
        elif node.child[0].data == 'return语句':
            self.proc_return_stmt(node.child[0])
        elif node.child[0].data == '结构体域声明语句':
            self.proc_struct_field_stmt(node.child[0])
        elif not node.child[0].is_valid():
            return
        self.proc_func_body_closure(node.child[1])

    def proc_dec_stmt(self, node):
        tp, val = self.proc_dec(node.child[0])
        self.proc_multi_var_dec_closure(node.child[1], tp)

    def var_defined(self, val_name):
        return self.variable_manager.find_variable(self.scope_manager.scopes, val_name) != -1

    def proc_assign_func(self, node):
        var_name, pos, attribute = self.proc_var(node.child[0])
        # 判断定义
        if node.child[1].child[0].data == '=':
            if not self.var_defined(var_name):
                err = Error(UndefinedError(var_name), pos)
                error_manager.add_error(err)
                return None

        self.proc_assign_or_func_call(node.child[1], var_name, attribute)

    def proc_if_stmt(self, node):
        label_if = new_label("if", node.id)
        self.proc_logic_exp(node.child[2]) # 处理表达式，并生成跳转语句
        self.instruction_manager.add_label(label_if) # 回填上一个跳转语句的跳转地址入口为label_if
        self.scope_manager.go_scope() # 更新作用域
        label_exit = new_label('exit', node.id) # 定义退出的出口label
        self.instruction_manager.add_instruction('goto', "", "", label_exit) # 生成跳转（隐式的else)
        self.instruction_manager.add_instruction('label', "", "", label_if) # 下面是if成立的内容
        self.proc_func_body(node.child[5])
        self.instruction_manager.add_instruction('goto', "", "", label_exit) # 退出if
        self.scope_manager.out_scope() # 退出if的作用域
        self.instruction_manager.add_instruction('label', "", "", label_exit) # 指定exit的入口从这里开始
        self.proc_else_stmt(node.child[-1]) # 显性的else


    def proc_while_loop(self, node):
        label_while = new_label("while", node.id)
        label_while_block = new_label("while_block", node.id)
        label_while_exit = new_label("EXIT", node.id)
        self.instruction_manager.add_instruction("label", "", "", label_while)
        self.proc_logic_exp(node.child[2])
        self.instruction_manager.add_label(label_while_block)
        self.instruction_manager.add_instruction('goto', "", "", label_while_exit)
        # print('label', label_while_block)
        self.instruction_manager.add_instruction('label', "", "", label_while_block)
        self.scope_manager.go_scope()
        self.proc_func_body(node.child[-2])
        self.instruction_manager.add_instruction('goto', "", "", label_while)
        self.instruction_manager.add_instruction('label', "", "", label_while_exit)
        self.scope_manager.out_scope()
    def proc_empty_stmt(self, node):
        pass

    def proc_return_stmt(self, node):
        v_obj = self.proc_factor_exp(node.child[1])
        self.instruction_manager.add_instruction('return', "", "", v_obj.reg);
        return v_obj

    def proc_multi_var_dec_closure(self, node, tp):
        if not node.child[0].is_valid():
            return
        self.proc_multi_var_dec(node.child[1], tp)
        self.proc_multi_var_dec_closure(node.child[2], tp)

    def proc_multi_var_dec(self, node, tp):
        var, pos, attr = self.proc_var(node.child[0])
        self.variable_manager.add_variable(self.scope_manager.cur, var, tp, pos)
        self.proc_init_value(node.child[1], var)

    def assign_value(self, var_name, v_obj, pos):
        target_scope, _ = self.variable_manager.find_variable(self.scope_manager.scopes, var_name)
        self.variable_manager.set_variable(target_scope, var_name, v_obj, pos)

    def assign_struct_value(self, var_name, v_obj, attribute, pos):
        target_scope, _ = self.variable_manager.find_variable(self.scope_manager.scopes, var_name)
        # self.variable_manager.set_variable(target_scope, var_name, v_obj, pos)
        self.variable_manager.set_struct_attribute(target_scope, self.scope_manager.scopes, var_name, attribute, v_obj,
                                                   pos)

    def proc_assign_or_func_call(self, node, var_name, attribute):
        if node.child[0].data == '=':
            v_obj = self.proc_rvalue(node.child[1])
            if v_obj:
                if attribute is None:
                    self.assign_value(var_name, v_obj, node.child[0].pos)
                    scope, obj = self.find_near_variable(var_name)
                    offset = obj.offset
                    self.instruction_manager.add_instruction('=', v_obj.reg, "", str(offset))
                else:
                    # TODO
                    self.assign_struct_value(var_name, v_obj, attribute, node.child[0].pos)
        else:
            # judge
            # TODO  函数的代码生成
            func = self.function_manager.get(var_name, node.child[0].pos)
            if func:
                # 判断参数类型是否一致
                func_name = var_name if var_name.startswith('get') else None
                func_name = None
                v_obj_list = self.proc_param_list(node.child[1], func_name)
                if not func:
                    return None
                # 确定参数类型是否匹配
                params_list = [e.type for e in v_obj_list]

                if not self.function_manager.params_match(var_name, params_list, node.child[0].pos):
                    # print(f"{func_name} parameter mis match")
                    return None

                # 生成函数调用的中间代码，这里只特殊处理 GET 和 PUT 方法
                if var_name.startswith('get'):
                    for param in v_obj_list:
                        param_name = param.id
                        scope, obj = self.find_near_variable(param_name)
                        offset = obj.offset
                        self.instruction_manager.add_instruction('get', "", "", str(offset))
                elif var_name == 'put':
                    # TODO 处理 put
                    self.instruction_manager.add_instruction('put', "", "", v_obj_list[0].reg)

    def proc_dec_closure(self, node, param_list):
        if node.child[0].is_valid():
            param_list.append(self.proc_dec(node.child[1]))
            return self.proc_dec_closure(node.child[2], param_list)
        else:
            return param_list

    def proc_logic_exp(self, node):
        if node.child[0].data == '!':
            v_obj = self.proc_exp(node.child[1])
            self.variable_manager.op_variable_single('!', v_obj, node.child[0].data)
        else:
            v_obj1 = self.proc_exp(node.child[0])
            op, pos = self.proc_logic_op(node.child[1])
            v_obj2 = self.proc_exp(node.child[2])
            res = self.instruction_manager.get_temp_reg()
            self.instruction_manager.add_instruction(op, v_obj1.reg, v_obj2.reg, res)
            self.variable_manager.op_variable(v_obj1, op, v_obj2, pos)
        pass

    def proc_else_stmt(self, node):
        if node.child[0].data == ';':
            return
        elif not node.child[0].is_valid():
            return
        elif node.child[0].data == 'else':
            # 首先先改变上个的跳转地址
            # label_else = new_label("else", node.id)
            # self.instruction_manager.add_label(label_else)
            # self.instruction_manager.add_instruction('label', "", "", label_else)
            self.scope_manager.go_scope()
            self.proc_func_body(node.child[2])
            self.scope_manager.out_scope()

        return

    def proc_logic_op(self, node):
        return node.child[0].data, node.child[0].pos

    def init_function_manager(self):
        # add std library functions
        fr = open("./resource/std_library_functions.txt", encoding='utf8')
        for func in fr:
            data = func.strip().split(" ")
            ret_type = TYPE(data[0])
            func_name = data[1]
            func_params = data[2:]
            func_params = [TYPE(e) for e in func_params]
            self.function_manager.add_func(ret_type, func_name, func_params)

    def print_function_table(self):
        print_line("function table")
        print(self.function_manager)
        print_line("end")
        print()

    def print_variable_table(self):
        print_line("variable table")
        print(self.variable_manager)
        print_line("end")
        print()

    def proc_bool_value(self, node):
        return node.child[0].data

    def proc_struct_field(self, node, var_name, pos):
        var_list = []
        var_list = self.proc_struct_filed_list(node.child[0], var_list)
        # print(var_list)
        # 得到了结构体域变proc_struct_field量列表后，加入到变量表中
        self.variable_manager.add_variable(self.scope_manager.cur, var_name, TYPE.struct, pos)
        # 对于结构体而言，值是多个变量
        self.set_struct_field(var_name, var_list, pos)

    def proc_struct_filed_list(self, node, var_list):
        if node.child[0].is_valid():
            # print(node)
            var_type, var_name = self.proc_struct_field_var(node.child[0])
            var_list.append((TYPE(var_type), var_name))
            self.proc_struct_filed_list(node.child[1], var_list)
            return var_list
        return var_list

    def proc_struct_field_var(self, node):
        var_type = self.proc_type(node.child[0])
        var_name = self.proc_user_symbol(node.child[1])
        return var_type, var_name

    def set_struct_field(self, var_name, var_list, pos):
        self.variable_manager.set_struct_field(self.scope_manager.cur, var_name, var_list, pos)
        #     可以查询是否出现冲突
        defined_vars = self.variable_manager.check_struct_field(self.scope_manager.cur, var_name)
        if defined_vars:
            print(f'[WARNING] struct {var_name} variable {defined_vars} have the same name as existing variable')

    def proc_struct_field_stmt(self, node):
        var_name, pos, attr = self.proc_user_symbol(node.child[1])
        self.proc_struct_impl(node.child[2], var_name, pos)

    def proc_struct_impl(self, node, var_name, pos):
        if node.child[0].data == '{':
            # 标识定义结构体
            self.proc_struct_field(node.child[1], var_name, pos)
        else:
            struct_var_name = node.child[0].symbol
            # TODO 应该在这里实现插入
            self.variable_manager.add_variable(self.scope_manager.cur, struct_var_name, TYPE.struct, pos, var_name)


def get_easy_tokens():
    tokens = [('id', '1'), ('+', ''), ('id', '2'), ('*', ''), ('id', '3'), ('$', '')]
    # tokens = [('*','',1), ('id','',2), ('*','',3),('+','',4),('id','',5)] # error
    return tokens


def test():
    lex = Lex()
    tokens = get_easy_tokens()

    grammar = Gram("./resource/cfg.txt")

    grammar.parse(tokens, pr=True)
    grammar.print_tree()
    simple_tree = ['E',
                   ['T',
                    ['F', 'id'],
                    'Ti'],
                   ['Ei',
                    '+',
                    ['T',
                     ['F', 'id'],
                     ['Ti', '*',
                      ['F', 'id'],
                      'Ti']],
                    'Ei']
                   ]

    # print(r == simple_tree)
    semantic = Semantic(grammar)
    tree = grammar.tree
    semantic.dfs(tree.root)


# 全局变量
error_manager = ErrorManager()

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
