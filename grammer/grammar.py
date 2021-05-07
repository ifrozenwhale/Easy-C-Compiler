import sys
import re
import pandas as pd
import numpy as np

sys.path.append('../lexical')
sys.path.append('../utils')
from lexical import Lex
from copy import deepcopy
from utils.log import Log

logger = Log("./logs/log.txt")


class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    @classmethod
    def print_bold(cls, x):
        print(Color.BOLD + x + Color.END)

    @classmethod
    def red_bold(cls, x):
        return Color.RED + Color.BOLD + x + Color.END

    @classmethod
    def blue_underline(cls, x):
        return Color.BLUE + Color.UNDERLINE + x + Color.END


def __get_tokens(filename):
    lex = Lex()
    token_list = lex.create_tokens(filename=filename)
    return token_list


def get_test_tokens(filename='../lexical/full_test.cpp'):
    # tokens = [('id', ''), ('+', ''), ('id', ''), ('*', ''), ('id', ''), ('$', '')]
    # tokens = [('*','',1), ('id','',2), ('*','',3),('+','',4),('id','',5)] # error
    tokens = __get_tokens(filename)
    tokens.append(('$', '', ''))
    return tokens


class Node:
    def __init__(self, data, symbol=None):
        self.data = data
        self.child = []
        self.symbol = symbol

    def add_child(self, child):
        self.child.insert(0, child)


class Tree:
    def __init__(self, root=None):
        self.root = root
        self.info = []

    def bfs(self):
        queue = [self.root]
        while len(queue) > 0:
            cnt = len(queue)
            tmp = []
            while cnt > 0:
                front = queue.pop(0)
                tmp.append(front.data)
                for node in front.child:
                    queue.append(node)
                cnt -= 1
            print(tmp)

    def print(self):
        self.dfs_showdir(self.root, 0)

    def save(self, save_path="./result/tree"):
        fw = open(save_path, encoding='utf8', mode='w')
        for i in self.info:
            fw.write(i + '\n')
        fw.close()

    def dfs_showdir(self, node, depth):
        if depth == 0:
            print("root:[" + node.data + "]")
        for item in node.child:
            leaf = len(item.child) == 0
            raw_info = '' if item.data == '#' else f' {item.data} @ {item.symbol}' if leaf else item.data
            info = '' if item.data == '#' else f' {Color.red_bold(item.data)} {Color.blue_underline(str(item.symbol))}' if leaf else item.data
            print("|      " * depth + "|--" + info)
            self.info.append("|      " * depth + "|--" + raw_info)
            if not leaf:
                self.dfs_showdir(item, depth + 1)


class Stack:
    def __init__(self) -> None:
        self.stack = []

    def push(self, x):
        self.stack.append(x)

    def pop(self):
        return self.stack.pop()

    def empty(self):
        return len(self.stack) == 0

    def top(self):
        return self.stack[-1]

    def size(self):
        return len(self.stack)

    def info(self):
        return str([e.data for e in self.stack])

    def end(self):
        return len(self.stack) == 1 and self.stack[0] == '$'


class Gram:

    def __init__(self, filepath='./cfg.txt') -> None:
        self.TERMINAL = set()
        self.NON_TERMINAL = set()
        self.NULLABLE = set()
        self.FIRST = dict()
        self.FOLLOW = dict()
        self.FIRST_S = dict()
        self.CFG = list()
        self.ANA_TABLE = dict()
        self.ERRORS = list()
        self.DFG_HASH = dict()
        self.START = ''
        self.init_cfg(filepath)
        self.init_nullable()
        self.init_first()
        self.init_follow()
        self.init_first_s()
        self.init_table()
        self.tree = Tree()

    def print_tree(self, save=None):
        self.tree.print()
        if save:
            self.tree.save(save)

    def init_cfg(self, filepath):
        print('hello')
        fr = open(filepath, encoding='utf8')

        idx = 0
        for line in fr:
            data = line.strip()
            data_list = data.split('->')
            data_list[0] = data_list[0][1:-1]
            self.NON_TERMINAL.add(data_list[0])
            if self.START == '':
                self.START = data_list[0]
            terminals = re.findall(r"[\[](.*?)[]]", data_list[1])
            for t in terminals:
                self.TERMINAL.add(t)
            # print(data_list[1])
            temp_list = re.findall(r"[\[](.*?)[]]|[<](.*?)[>]", data_list[1])
            item_list = [e[0] if e[0] != '' else e[1] if e[1] != '' else '' for e in temp_list]
            # item_list = []
            # for item in temp_list:
            #     if item[0] != '':
            #         item_list.append(item[0])
            #     elif item[1] != '':
            #         item_list.append(item[1])
            # print(item_list)
            # item_list += re.findall(r"[\[](.*?)[]]", data_list[1])
            # item_list = [e for e in item_list if e != '']
            # item_list = list(filter(lambda x: x, re.split(r"[>\]]", re.sub(r"[<\[]", '', data_list[1]))))
            self.CFG.append((str(idx), data_list[0], item_list))
            self.DFG_HASH[idx] = (str(idx), data_list[0], item_list)
            idx += 1

    def is_non_terminal_list(self, beta):
        for b in beta:
            if b not in self.NON_TERMINAL:
                return False
        return True

    def is_nullable_list(self, beta):
        for b in beta:
            if b not in self.NULLABLE:
                return False
        return True

    def init_nullable(self):
        while True:
            last_size = len(self.NULLABLE)
            for idx, X, beta in self.CFG:
                if beta[0] == '#':
                    self.NULLABLE.add(X)
                if self.is_non_terminal_list(beta):
                    if self.is_nullable_list(beta):
                        self.NULLABLE.add(X)
            if last_size == len(self.NULLABLE):
                break

    def init_first(self):
        for N in self.NON_TERMINAL:
            self.FIRST[N] = set()
        while True:
            last_set = deepcopy(self.FIRST)
            for idx, N, beta in self.CFG:
                for b in beta:
                    if b in self.TERMINAL:
                        self.FIRST[N].add(b)
                        break
                    if b in self.NON_TERMINAL:
                        self.FIRST[N] |= self.FIRST[b]
                        if b not in self.NULLABLE:
                            break
            if last_set == self.FIRST:
                break

    def create_analysis_table(self):
        for p in self.CFG:
            idx, A, beta = p
            for b in self.FIRST_S[idx]:
                if b != '#':
                    self.ANA_TABLE[A][b].add(idx)

            if '#' in self.FIRST_S[idx]:
                for b in self.FOLLOW[A]:
                    if b != '#':
                        # print(p)
                        self.ANA_TABLE[A][b].add(idx)
        for NT in self.NON_TERMINAL:
            for b in self.FOLLOW[NT]:
                if len(self.ANA_TABLE[NT][b]) == 0:
                    self.ANA_TABLE[NT][b].add('synch')

    def init_follow(self):
        for N in self.NON_TERMINAL:
            self.FOLLOW[N] = set()
        self.FOLLOW[self.START].add('$')
        while True:
            last_set = deepcopy(self.FOLLOW)
            for idx, N, beta in self.CFG:
                # ERROR HERE
                temp = deepcopy(self.FOLLOW[N])
                for b in beta[::-1]:
                    if b in self.TERMINAL:
                        temp = {b}
                    if b in self.NON_TERMINAL:
                        # if b == 'E':
                        #     print('[DEBUG]', self.FOLLOW[b], N, beta, temp)
                        # print("temp p", N, beta, '      b', b, temp)
                        self.FOLLOW[b] |= temp
                        if b not in self.NULLABLE:
                            temp = self.FIRST[b]
                        else:
                            temp |= self.FIRST[b]
            if last_set == self.FOLLOW:
                break
        for item in self.FOLLOW.items():
            if '#' in item[1]:
                item[1].remove('#')

    def calculate_first_s(self, p):
        idx, N, beta = p
        for b in beta:
            if b in self.TERMINAL:
                self.FIRST_S[idx].add(b)
                if b != '#':
                    return
            if b in self.NON_TERMINAL:
                self.FIRST_S[idx] |= self.FIRST[b]
                if b not in self.NULLABLE:
                    return
        self.FIRST_S[idx] |= self.FOLLOW[N]

    def init_first_s(self):
        for idx, x, beta in self.CFG:
            self.FIRST_S[idx] = set()
        for p in self.CFG:
            self.calculate_first_s(p)

    def init_table(self):
        for N in self.NON_TERMINAL:
            self.ANA_TABLE[N] = {}
            for T in self.TERMINAL:
                self.ANA_TABLE[N][T] = set()
            self.ANA_TABLE[N]['$'] = set()

    def print_table(self):

        text_width = 30
        header = [""] + list(list(self.ANA_TABLE.values())[0].keys())
        for h in header:
            print("@{:20}".format(h), end='')
        print()
        for NT, TL in self.ANA_TABLE.items():
            print("@{:20}".format(NT), end='')
            for T in TL:
                print(self.ANA_TABLE[NT][T], end='    ')
            print()

    def save_table(self, save_path="./results/table.csv"):
        header = ["non_terminal"] + list(list(self.ANA_TABLE.values())[0].keys())
        df = pd.DataFrame(columns=header)
        for NT, TL in self.ANA_TABLE.items():
            line = list(TL.values())
            line = [e if len(e) > 0 else '' for e in line]
            df.loc[len(df)] = [NT] + line
            # for T in TL:
            #     print(self.ANA_TABLE[NT][T], end='    ')
        df.to_csv(save_path, index=False)

    def print_cfg(self):
        for idx, p in self.DFG_HASH.items():
            print(idx, p[1], '->', p[2])

    def phrase(self, tokens):
        logger.debug('-' * 100)
        self.create_analysis_table()
        self.print_table()
        self.tree.root = Node(self.START)
        curr_node = self.tree.root
        stack = Stack()
        stack.push(Node('$'))
        stack.push(curr_node)
        i = 0

        while not stack.empty():
            if i >= len(tokens):
                logger.error("illegal end of program")
                return
            print('[STACK] {:40}'.format(stack.info()), end='')
            print('[INPUT] {:40}'.format(tokens[i][0]), end='')
            node_t = stack.top()
            t = node_t.data
            if t in self.TERMINAL and t != '#' or t == '$':
                if t == tokens[i][0]:
                    # add token attribute
                    node_t.symbol = tokens[i][1]
                    i += 1
                    print()
                    # print('[DEBUG] solve', t, 'now i = ', i)
                    stack.pop()
                else:
                    logger.error(f' at line {tokens[i][2]},  expected {t} but received {tokens[i][0]}, move pointer')
                    # self.error(i, 'in terminal but mismatch')
                    stack.pop()
            else:
                # print('i=',i,'stack',stack.info())
                ich = tokens[i][0]
                table_item = self.ANA_TABLE[t][ich]
                if len(table_item) == 0:
                    # print(t, self.ANA_TABLE[t])
                    print(tokens)
                    logger.error(f'at line {tokens[i][2]}, cannot parse {t} when receiving {ich}, move pointer')
                    i += 1
                    continue
                if list(table_item)[0] == 'synch':
                    logger.error(f'at line {tokens[i][2]}, cannot parse {t} when receiving {ich}, pop {t}')
                    stack.pop()
                    continue
                stack.pop()
                unique_dfg_id = int(list(table_item)[0])
                _, dfg_l, dfg_r = self.DFG_HASH[unique_dfg_id]
                curr_node = node_t
                for ch in dfg_r[::-1]:
                    ch_node = Node(ch)
                    curr_node.add_child(ch_node)
                    if ch != '#':
                        stack.push(ch_node)
                print('[OUTPUT]', self.DFG_HASH[unique_dfg_id])

    def error(self, l, i, info):
        print(f"\n[ERROR] at line {l}, char at {i} of total, {info}")


if __name__ == '__main__':
    # grammar = Gram('test_cfg1.txt')
    grammar = Gram("cfg_resource/cfg_v6.txt")
    # print(grammar.NULLABLE)
    # grammar.print_cfg()
    # print(grammar.FIRST)
    # print(grammar.FOLLOW)
    # print(grammar.FIRST_S)
    tokens = get_test_tokens("../lexical/error_demo.cpp")
    grammar.phrase(tokens)
    grammar.print_tree(save="./results/tree.txt")
    grammar.save_table()
