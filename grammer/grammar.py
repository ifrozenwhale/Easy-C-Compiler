import sys
import re

sys.path.append('../lexical')
from lexical import Lex
from copy import deepcopy


def get_tokens(filename='../lexical/test.cpp'):
    lex = Lex()
    token_list = lex.create_tokens(filename=filename)
    return token_list


def get_test_tokens():
    # tokens = [['id', ''], ('+', ''), ('id', ''), ('*', ''), ('id', ''), ('$', '')]
    tokens = get_tokens()
    tokens.append(('$', ''))
    return tokens


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
        return str(self.stack)

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

    def print_cfg(self):
        for idx, p in grammar.DFG_HASH.items():
            print(idx, p[1], '->', p[2])

    def phrase(self):
        self.create_analysis_table()
        self.print_table()
        tokens = get_test_tokens()
        print(tokens)
        stack = Stack()
        stack.push('$')
        stack.push(self.START)
        i = 0
        output_info = ''
        output_flag = False
        while not stack.empty():
            print('[STACK] {:40}'.format(stack.info()), end='')
            print('[INPUT] {:40}'.format(tokens[i][0]), end='')
            t = stack.top()
            if t in self.TERMINAL and t != '#' or t == '$':
                if t == tokens[i][0]:
                    i += 1
                    print()
                    # print('[DEBUG] solve', t, 'now i = ', i)
                    stack.pop()
                else:
                    self.error(i, 'in terminal but mismatch')
            else:
                # print('i=',i,'stack',stack.info())
                ich = tokens[i][0]
                table_item = self.ANA_TABLE[t][ich]
                if len(self.ANA_TABLE[t][ich]) == 0:
                    print(t,self.ANA_TABLE[t])
                    self.error(i, 'in non terminal but empty')
                stack.pop()
                unique_dfg_id = int(list(table_item)[0])
                dfg = self.DFG_HASH[unique_dfg_id][2]
                for ch in dfg[::-1]:
                    if ch != '#':
                        stack.push(ch)
                print('[OUTPUT]', self.DFG_HASH[unique_dfg_id])

    def error(self, i, info):
        print("\nerror takens", i, info)
        exit(-1)


if __name__ == '__main__':
    # grammar = Gram()
    grammar = Gram("./cfg_v5.txt")
    # print(grammar.NULLABLE)
    # grammar.print_cfg()
    # print(grammar.FIRST)
    # print(grammar.FOLLOW)
    # print(grammar.FIRST_S)

    grammar.phrase()
