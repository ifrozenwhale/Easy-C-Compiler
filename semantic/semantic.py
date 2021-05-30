import sys
import re
import pandas as pd
import numpy as np

sys.path.append('../lexical')
sys.path.append('../utils')
sys.path.append('../grammar')
from lexical import Lex
from copy import deepcopy
from log import Log
from grammar import Gram, get_test_tokens

logger = Log("./logs/log.txt")
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)
# 设置value的显示长度为100，默认为50
pd.set_option('max_colwidth', 200)
pd.set_option('display.width', 5000)
from enum import Enum


class TYPE(Enum):
    bool = "bool"
    int = "int"
    char = "char"
    void = "void"


class ErrorType(Enum):
    undefined = 0
    multi_defined = 1


class Variable:
    def __init__(self, tp=None, val=None, id=None):
        self.id = id
        self.type = tp
        self.val = val

    def __add__(self, other):
        return Variable(self.type, self.val + other.val)

    def __sub__(self, other):
        return Variable(self.type, self.val - other.val)

    def __mul__(self, other):
        return Variable(self.type, self.val * other.val)

    def __truediv__(self, other):
        return Variable(self.type, self.val / other.val)

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

    def __repr__(self):
        vid = self.id + ',' if self.id else ''
        return "({}{},{})".format(vid, self.type, self.val)


class Error:
    def __int__(self, tp, details):
        self.type = tp
        self.details = details


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
        return self.variables[scope][v]

    def find_variable(self, scope_list, v):
        for scope in scope_list[::-1]:
            if self.contains(scope, v):
                return scope, self.variables[scope][v]
        print("undefined v {}.".format(v))
        return -1

    def add_variable(self, scope, v, tp):
        if self.contains(scope, v):
            print("v {} is already defined".format(v));
            return -1
        if scope not in self.variables:
            self.variables[scope] = {}
        self.variables[scope][v] = Variable(tp=TYPE(tp), id=v)
        return 0

    def set_variable(self, scope, v, v_obj):
        old_v = self.get_variable(scope, v)
        if v_obj.type != old_v.type:
            print("{} {} cannot assign\n".format(old_v, v_obj))
            return -1
        if not v_obj.val:
            print("{} not initialized\n".format(v_obj))
            return -1
        old_v.val = v_obj.val

    def op_variable(self, x, op, y):
        err_type = None
        if not x.val:
            print("{} not initialized".format(x))
            err_type = 1
        if not y.val:
            print("{} not initialized".format(y))
            err_type = 1
        if x.type != y.type:
            print("cannot op \n")
            err_type = 2
        if err_type:
            return None
        if op == '+':
            return x + y
        elif op == '-':
            return x - y
        elif op == '*':
            return x * y
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
            return x or y
        elif op == '&&':
            return x and y

    def __str__(self):
        res = []
        for v_obj in self.variables.values():
            res.append(str(v_obj))
        return "\n".join(res)


class Function:
    def __init__(self):
        self.ret_type = None
        self.params = []

    def __init__(self, ret_type, name, params):
        self.ret_type = ret_type
        self.name = name
        self.params = params

    def __repr__(self):
        return "{} {} {}".format(self.ret_type, self.name, str(self.params))


class FunctionManager:
    def __init__(self):
        self.func_map = {}

    def add_func(self, ret_type, func_name, params):
        if func_name in self.func_map:
            print("function {} is already defined".format(func_name))
            return -1
        self.func_map[func_name] = Function(ret_type, func_name, params)

    def __repr__(self):
        ret = []
        for func in self.func_map.values():
            ret.append(str(func))
        return str(ret)
    def get(self, func_name):
        if func_name in self.func_map:
            return self.func_map[func_name]
        print(f"function {func_name} undefined")
        return None
    def params_match(self, func_name, params):
        func = self.func_map[func_name]
        std_params = [e[0] for e in func.params]
        print(std_params,params)
        return std_params == params
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


class Semantic:
    def __init__(self, tree):
        self.tree = tree
        self.variable_manager = VariableManager()
        self.function_manager = FunctionManager()
        self.scope_manager = ScopeManager()
        self.init_function_manager()

    def run(self):
        self.tree.print()
        self.proc_program(self.tree.root)
        print(self.variable_manager)
        print(self.function_manager)

    def proc_program(self, root):
        self.scope_manager.set_global(0)
        self.scope_manager.go_scope()

        self.proc_func_or_dec_list(root.child[0])

    def proc_func_or_dec_list(self, node):
        if node.child[0].is_valid():
            self.proc_func_or_dec(node.child[0])
            self.proc_func_or_dec_list(node.child[1])

    def proc_func_or_dec(self, node):
        tp, var = self.proc_type_var(node.child[0])
        self.proc_param_impl_or_var_dec(node.child[1], tp, var)

    def proc_type_var(self, node):
        tp = self.proc_type(node.child[0])
        var = self.proc_var(node.child[1])
        self.variable_manager.add_variable(self.scope_manager.cur, var, tp)
        return tp, var

    def proc_type(self, node):
        return node.child[0].data

    def proc_var(self, node):
        if node.child[0].data == '标识符':
            sym = self.proc_user_symbol(node.child[0])
        else:
            sym = self.proc_system_symbol(node.child[0])
        return sym

    def proc_user_symbol(self, node):
        return node.child[0].symbol

    def proc_system_symbol(self, node):
        # 标准库函数
        return node.child[0].symbol

    def proc_param_impl_or_var_dec(self, node, tp, var):
        if node.child[0].data == '(':
            # 如果判断为函数，则需要将 变量表 中的变量拿出来，放进函数表中
            self.variable_manager.delete_variable(self.scope_manager.cur, var)
            self.scope_manager.go_scope()
            # print('cur', self.scope_manager.cur, end='\n')
            params = self.proc_param_dec(node.child[1])

            self.function_manager.add_func(TYPE(tp), var, params)

            # 要进入代码段了
            self.proc_func_impl(node.child[3])
        else:
            # print(node.child)
            self.proc_global_var_closure(node.child[0], tp)

    def proc_global_var_closure(self, node, tp):
        for child in node.child:
            if child.data == ';':
                break
            elif child.data == '变量':
                var_name = self.proc_var(child)
                self.variable_manager.add_variable(self.scope_manager.cur, var_name, tp)
                return
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
        var_name = self.proc_var(node.child[1])
        self.variable_manager.add_variable(self.scope_manager.cur, var_name, tp)
        self.proc_init_value(node.child[2], var_name)
        return TYPE(tp), var_name

    def proc_init_value(self, node, v):
        if node.child[0].data == '=':
            v_obj = self.proc_rvalue(node.child[1])
            # 赋值
            if v_obj:
                self.assign_value(v, v_obj)
        else:
            return

    def proc_rvalue(self, node) -> Variable:
        return self.proc_exp(node.child[0])

    def proc_exp(self, node):
        v_obj = self.proc_factor_item(node.child[0])
        v_item = self.proc_item(node.child[1], v_obj)
        # TODO 处理因子和项
        # print('v_obj', v_obj, 'item', v_item)
        return v_item

    def proc_factor_item(self, node):
        v_obj = self.proc_factor_exp(node.child[0])
        return self.proc_factor_exp_closure(node.child[1], v_obj)

    def proc_item(self, node, item):
        if node.child[0].is_valid():
            v_obj = self.proc_factor_item(node.child[1])
            item = self.variable_manager.op_variable(item, node.child[0].data, v_obj)
            item = self.proc_item(node.child[2], item)
            return item
        return item

    def find_near_variable(self, var_name):
        return self.variable_manager.find_variable(self.scope_manager.scopes, var_name)

    def proc_factor_exp(self, node):
        if node.child[0].is_terminal():  # (表达式)
            return self.proc_exp(node.child[1])
        elif node.child[0].data == '数字':
            num = self.proc_digit(node.child[0])
            return Variable(TYPE.int, num)
        elif node.child[0].data == '变量':
            var_name = self.proc_var(node.child[0])
            if not node.child[1].child[0].is_valid():
                if not self.var_defined(var_name):
                    return None
                _, v_obj = self.find_near_variable(var_name)
                return v_obj
            else:
                v_obj_list = self.proc_func_call_param(node.child[1])
                # TODO 处理函数调用结果计算
                print('v_obj_list', v_obj_list)
                func_name = var_name
                func = self.function_manager.get(func_name)
                if not func:
                    return None
                # 确定参数类型是否匹配
                params_list = [e.type for e in v_obj_list]

                if not self.function_manager.params_match(func_name, params_list):
                    print(f"{func_name} parameter mis match")
                    return None

                return Variable(tp=func.ret_type)


    def proc_factor_exp_closure(self, node, factor_exp):
        if node.child[0].is_valid():
            v_obj = self.proc_factor_exp(node.child[1])
            factor_exp = self.variable_manager.op_variable(factor_exp, node.child[0].data, v_obj)
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

    def proc_param_list(self, node):
        v_obj = self.proc_param(node.child[0])
        v_obj_list = self.proc_param_closure(node.child[1], [v_obj])
        return v_obj_list

    def proc_param(self, node):
        if node.child[0].data == '标志符':
            var_name = self.proc_user_symbol(node.child[0])
            scope, v_obj = self.find_near_variable(var_name)
            return v_obj
        elif node.child[0].data == '数字':
            return self.proc_digit(node.child[0])

    def proc_param_closure(self, node, v_obj_list):
        if node.child[0].data == ',':
            val = self.proc_param(node.child[1])
            v_obj_list.append(val)

            return self.proc_param_closure(node.child[2], v_obj_list)
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
        elif not node.child[0].is_valid():
            return
        self.proc_func_body_closure(node.child[1])

    def proc_dec_stmt(self, node):
        tp, val = self.proc_dec(node.child[0])
        self.proc_multi_var_dec_closure(node.child[1], tp)

    def var_defined(self, val_name):
        return self.variable_manager.find_variable(self.scope_manager.scopes, val_name) != -1

    def proc_assign_func(self, node):
        var_name = self.proc_var(node.child[0])
        # 判断定义
        if not self.var_defined(var_name):
            return None
        self.proc_assign_or_func_call(node.child[1], var_name)

    def proc_while_loop(self, node):
        self.proc_logic_op(node.child[2])
        self.scope_manager.go_scope()
        self.proc_func_body(node.child[-2])
        self.scope_manager.out_scope()

    def proc_if_stmt(self, node):
        self.proc_logic_exp(node.child[2])
        self.scope_manager.go_scope()
        self.proc_func_body(node.child[5])
        self.scope_manager.out_scope()
        self.proc_else_stmt(node.child[-1])

    def proc_empty_stmt(self, node):
        pass

    def proc_return_stmt(self, node):
        v_obj = self.proc_factor_exp(node.child[1])
        return v_obj

    def proc_multi_var_dec_closure(self, node, tp):
        if not node.child[0].is_valid():
            return
        self.proc_multi_var_dec(node.child[1], tp)
        self.proc_multi_var_dec_closure(node.child[2], tp)

    def proc_multi_var_dec(self, node, tp):
        var = self.proc_var(node.child[0])
        self.variable_manager.add_variable(self.scope_manager.cur, var, tp)

        self.proc_init_value(node.child[1], var)

    def assign_value(self, var_name, v_obj):
        target_scope, _ = self.variable_manager.find_variable(self.scope_manager.scopes, var_name)
        self.variable_manager.set_variable(target_scope, var_name, v_obj)

    def proc_assign_or_func_call(self, node, var_name):
        if node.child[0].data == '=':
            v_obj = self.proc_rvalue(node.child[1])
            if v_obj:
                self.assign_value(var_name, v_obj)
        else:
            # TODO func call
            self.proc_param_list(node.child[1])

    def proc_dec_closure(self, node, param_list):
        if node.child[0].is_valid():
            param_list.append(self.proc_dec(node.child[1]))
            return self.proc_dec_closure(node.child[2], param_list)
        else:
            return param_list

    def proc_logic_exp(self, node):
        if node.child[0].data == '!':
            self.proc_exp(node.child[1])
        else:
            v_obj1 = self.proc_exp(node.child[0])
            op = self.proc_logic_op(node.child[1])
            v_obj2 = self.proc_exp(node.child[2])
            self.variable_manager.op_variable(v_obj1, op, v_obj2)
        pass

    def proc_else_stmt(self, node):
        if node.child[0].data == ';':
            return
        elif not node.child[0].is_valid():
            return
        elif node.child[0].data == 'else':
            self.scope_manager.go_scope()
            self.proc_func_body(node.child[2])
            self.scope_manager.out_scope()
        return

    def proc_logic_op(self, node):
        return node.child[0].data

    def init_function_manager(self):
        # add std library functions
        fr = open("./resource/std_library_functions.txt", encoding='utf8')
        for func in fr:
            data = func.strip().split(" ")
            ret_type = TYPE(data[0])
            func_name = data[1]
            func_params = data[2:]
            self.function_manager.add_func(ret_type, func_name, func_params)


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


if __name__ == '__main__':
    # test()

    lex = Lex()

    tokens = get_test_tokens("../lexical/easy_test.cpp")
    grammar = Gram("../grammar/cfg_resource/cfg_v7.txt")

    grammar.parse(tokens, pr=False)
    #
    semantic = Semantic(grammar.tree)
    semantic.run()
